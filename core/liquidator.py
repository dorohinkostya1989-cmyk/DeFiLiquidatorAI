"""
Liquidation executor using FlashLiquidator contract
Dynamic gas pricing and private mempool support
"""

import logging
from web3 import Web3
from core.config import (
    PRIVATE_KEY, LIQUIDATOR_CONTRACT, RPC_URL, RPC_URL_BACKUP,
    MIN_PROFIT_USD, DEFAULT_POOL_FEE, AGGRESSIVE_MODE, PRIVATE_MEMPOOL
)
from core.helpers import estimate_profit

log = logging.getLogger(__name__)

LIQUIDATOR_ABI = [
    {
        "inputs": [
            {"name": "collateralAsset", "type": "address"},
            {"name": "debtAsset", "type": "address"},
            {"name": "user", "type": "address"},
            {"name": "debtToCover", "type": "uint256"},
            {"name": "poolFee", "type": "uint24"},
        ],
        "name": "liquidate",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"name": "token", "type": "address"}],
        "name": "withdrawToken",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "withdrawMatic",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]


class LiquidationExecutor:
    """Executes liquidations via FlashLiquidator contract"""

    def __init__(self):
        self.w3 = self._connect()
        self.account = self.w3.eth.account.from_key(PRIVATE_KEY)
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(LIQUIDATOR_CONTRACT),
            abi=LIQUIDATOR_ABI,
        )
        log.info(f"Wallet: {self.account.address}")
        log.info(f"Contract: {LIQUIDATOR_CONTRACT}")

    def _connect(self) -> Web3:
        for url in [RPC_URL, RPC_URL_BACKUP]:
            try:
                w3 = Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": 30}))
                if w3.is_connected():
                    log.info(f"Connected: {url[:50]}...")
                    return w3
            except Exception:
                pass
        raise ConnectionError("No working RPC connection")

    def get_dynamic_gas(self, debt_usd: float) -> dict:
        """Dynamic gas pricing based on position size"""
        try:
            block = self.w3.eth.get_block("latest")
            base_fee = block.get("baseFeePerGas", self.w3.eth.gas_price)
        except Exception:
            base_fee = self.w3.eth.gas_price

        if AGGRESSIVE_MODE and debt_usd > 1000:
            fee_mult = 10.0
            tip_gwei = 100
        elif debt_usd > 1000:
            fee_mult = 2.0
            tip_gwei = 60
        elif debt_usd > 100:
            fee_mult = 1.5
            tip_gwei = 30
        else:
            fee_mult = 1.2
            tip_gwei = 15

        priority_fee = int(tip_gwei * 1e9)
        max_fee = int(base_fee * fee_mult) + priority_fee

        log.debug(
            f"Gas: base={base_fee/1e9:.1f} gwei | "
            f"maxFee={max_fee/1e9:.1f} gwei | "
            f"tip={tip_gwei} gwei | "
            f"mult={fee_mult}x (debt ${debt_usd:.0f})"
        )
        return {
            "maxFeePerGas": max_fee,
            "maxPriorityFeePerGas": priority_fee,
        }

    def execute_liquidation(self, params: dict) -> str | None:
        """Execute liquidation via FlashLiquidator"""
        profit = estimate_profit(params.get("total_debt_usd", 0))
        
        if profit < MIN_PROFIT_USD:
            log.info(f"Skipping - profit ${profit:.2f} < ${MIN_PROFIT_USD}")
            return None

        debt_usd = params.get("total_debt_usd", 0)
        log.info(
            f"Liquidating: user={params['user'][:12]}... | "
            f"HF={params.get('health_factor', 0):.4f} | "
            f"debt=${debt_usd:.2f} | profit≈${profit:.2f}"
        )

        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address, "pending")
            gas_args = self.get_dynamic_gas(debt_usd)

            tx = self.contract.functions.liquidate(
                Web3.to_checksum_address(params["collateral_asset"]),
                Web3.to_checksum_address(params["debt_asset"]),
                Web3.to_checksum_address(params["user"]),
                params["debt_to_cover"],
                DEFAULT_POOL_FEE,
            ).build_transaction({
                "from": self.account.address,
                "nonce": nonce,
                "gas": 900000,
                **gas_args,
            })

            signed = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            tx_hex = tx_hash.hex()
            if not tx_hex.startswith("0x"):
                tx_hex = "0x" + tx_hex

            log.info(f"TX sent: https://polygonscan.com/tx/{tx_hex}")

            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            if receipt.status == 1:
                log.info(f"SUCCESS! Gas used={receipt.gasUsed:,}")
                return tx_hex
            else:
                log.error(f"REVERT: {tx_hex}")
                return None

        except Exception as e:
            log.error(f"Liquidation error: {e}")
            return None

    def withdraw_profits(self, token_address: str):
        """Withdraw earned tokens to wallet"""
        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            gas_args = self.get_dynamic_gas(0)
            tx = self.contract.functions.withdrawToken(
                Web3.to_checksum_address(token_address)
            ).build_transaction({
                "from": self.account.address,
                "nonce": nonce,
                "gas": 150000,
                **gas_args,
            })
            signed = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            log.info(f"Withdraw: https://polygonscan.com/tx/{tx_hash.hex()}")
        except Exception as e:
            log.error(f"Withdraw error: {e}")
