"""
DeFiLiquidatorAI - Main entry point
AI-powered liquidation bot for Aave v3
"""

import json
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

from web3 import Web3
from dotenv import load_dotenv

from core.config import MIN_PROFIT_USD, PRIVATE_KEY, NETWORK, CHECK_INTERVAL
from core.helpers import estimate_profit
from core.monitor import WebSocketMonitor
from core.liquidator import LiquidationExecutor

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout),
    ]
)
log = logging.getLogger(__name__)

# Data directory
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

BORROWERS_FILE = DATA_DIR / "borrowers.json"
HF_CACHE_FILE = DATA_DIR / "hf_cache.json"

# Wallet address from private key
try:
    WALLET_ADDR = Web3().eth.account.from_key(PRIVATE_KEY).address
except Exception:
    WALLET_ADDR = "0x0000000000000000000000000000000000000000"


def load_json(path: Path, default):
    """Load JSON file or return default"""
    try:
        if path.exists():
            return json.loads(path.read_text())
    except Exception:
        pass
    return default


def save_json(path: Path, data):
    """Save data to JSON file"""
    try:
        path.write_text(json.dumps(data, indent=2))
    except Exception as e:
        log.debug(f"Save error: {e}")


def main():
    log.info("=" * 50)
    log.info("DeFiLiquidatorAI - AI-powered liquidation bot")
    log.info(f"Network: {NETWORK}")
    log.info(f"Wallet: {WALLET_ADDR}")
    log.info(f"Min profit: ${MIN_PROFIT_USD}")
    log.info("=" * 50)

    executor = LiquidationExecutor()

    # Load cached borrowers
    borrowers = set(load_json(BORROWERS_FILE, []))
    log.info(f"Loaded {len(borrowers)} borrowers from cache")

    # Connect to Web3
    w3 = executor.w3
    monitor = WebSocketMonitor(w3, borrowers, threading.Lock())
    
    log.info("Bot is running. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(CHECK_INTERVAL)
            log.info(f"Checking positions... (borrowers: {len(borrowers)})")
            
            # Save cache periodically
            save_json(BORROWERS_FILE, list(borrowers))
            
    except KeyboardInterrupt:
        log.info("Stopping bot...")
    except Exception as e:
        log.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
