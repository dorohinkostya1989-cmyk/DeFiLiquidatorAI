"""
Configuration loader for DeFiLiquidatorAI
All sensitive data is loaded from environment variables
"""

import os
from dotenv import load_dotenv

load_dotenv()

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
LIQUIDATOR_CONTRACT = os.getenv("LIQUIDATOR_CONTRACT")
RPC_URL = os.getenv("RPC_URL")
RPC_URL_BACKUP = os.getenv("RPC_URL_BACKUP")
NETWORK = os.getenv("NETWORK", "polygon")
MIN_PROFIT_USD = float(os.getenv("MIN_PROFIT_USD", "5.0"))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "15"))
AGGRESSIVE_MODE = os.getenv("AGGRESSIVE_MODE", "false").lower() == "true"
PRIVATE_MEMPOOL = os.getenv("PRIVATE_MEMPOOL", "true").lower() == "true"

AAVE_POOL_ADDRESS = "0x794a61358D6845594F94dc1DB02A252b5b4814aD"
AAVE_UI_PROVIDER = "0xC69728f11E9E6127733751c8410432913123acf1"
AAVE_SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/aave/protocol-v3-polygon"

TOKENS = {
    "USDC": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
    "USDT": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
    "DAI": "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
    "WETH": "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
    "WBTC": "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6",
    "WMATIC": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
    "AAVE": "0xD6DF932A45C0f255f85145f286eA0b292B21C90B",
    "LINK": "0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39",
}
