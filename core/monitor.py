"""
Real-time position monitoring for Aave v3
WebSocket connection for new blocks and liquidation events
"""

import json
import logging
import threading
import time
from typing import Dict, List, Optional, Set

from web3 import Web3
from core.config import (
    RPC_URL, RPC_URL_BACKUP, AAVE_POOL_ADDRESS, 
    NETWORK, CHECK_INTERVAL
)
from core.helpers import parse_health_factor, parse_debt

log = logging.getLogger(__name__)

WS_URL = RPC_URL.replace("https://", "wss://")

BORROW_TOPIC = Web3.keccak(text="Borrow(address,address,address,uint256,uint8,uint256,uint16)").hex()
LIQUIDATION_TOPIC = Web3.keccak(text="LiquidationCall(address,address,address,uint256,uint256,address,bool)").hex()

POOL_ABI = [{
    "inputs": [{"name": "user", "type": "address"}],
    "name": "getUserAccountData",
    "outputs": [
        {"name": "totalCollateralBase", "type": "uint256"},
        {"name": "totalDebtBase", "type": "uint256"},
        {"name": "availableBorrowsBase", "type": "uint256"},
        {"name": "currentLiquidationThreshold", "type": "uint256"},
        {"name": "ltv", "type": "uint256"},
        {"name": "healthFactor", "type": "uint256"},
    ],
    "stateMutability": "view",
    "type": "function",
}]


class WebSocketMonitor:
    """Real-time WebSocket monitor for Aave positions"""
    
    def __init__(self, w3: Web3, borrowers: Set[str], lock: threading.Lock):
        self.w3 = w3
        self.pool = w3.eth.contract(
            address=Web3.to_checksum_address(AAVE_POOL_ADDRESS), 
            abi=POOL_ABI
        )
        self._borrowers = borrowers
        self._lock = lock
        self._running = False
        self._connected = False
        
    def start(self):
        """Start WebSocket listener in background thread"""
        self._running = True
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()
        
    def stop(self):
        self._running = False
        
    @property
    def is_connected(self) -> bool:
        return self._connected
        
    def get_health_factor(self, user: str) -> tuple:
        """Get health factor and debt for a user"""
        try:
            data = self.pool.functions.getUserAccountData(
                Web3.to_checksum_address(user)
            ).call()
            hf = parse_health_factor(data[5])
            debt_usd = parse_debt(data[1])
            return hf, debt_usd
        except Exception as e:
            log.debug(f"HF check failed for {user}: {e}")
            return 999.0, 0.0
            
    def _listen(self):
        """WebSocket listener loop"""
        log.info(f"Starting WebSocket monitor for {NETWORK}")
        # Full WebSocket implementation will be added in next iteration
        pass
