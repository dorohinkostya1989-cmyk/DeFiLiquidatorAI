"""
AI Chat Interface for DeFiLiquidatorAI
Run with: python agent_chat.py
"""

import os
import sys
import logging
from dotenv import load_dotenv
from web3 import Web3

from core.config import RPC_URL, NETWORK
from core.monitor import WebSocketMonitor
from core.liquidator import LiquidationExecutor
from agent.client import ClaudeClient
from agent.executor import LiquidationExecutorAgent

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

def main():
    print("=" * 60)
    print("🤖 DeFiLiquidatorAI - AI Chat Interface")
    print("=" * 60)
    print("\nExamples:")
    print("  > Liquidate 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEbA on Base")
    print("  > Check 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEbA on Polygon")
    print("  > Liquidate if profit > $10")
    print("\nType 'exit' to quit\n")
    
    # Connect to blockchain
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("❌ Cannot connect to blockchain. Check RPC_URL in .env")
        return
    
    # Initialize components
    monitor = WebSocketMonitor(w3, set(), threading.Lock())
    liquidator = LiquidationExecutor()
    agent = LiquidationExecutorAgent(w3, monitor, liquidator)
    
    # Optional Claude AI
    claude = ClaudeClient()
    if claude.client:
        print("✅ Claude AI connected. Type natural language commands.")
    else:
        print("⚠️ Claude AI disabled (API key missing). Using regex parser.")
    
    while True:
        try:
            command = input("\n💬 You: ").strip()
            if command.lower() in ['exit', 'quit']:
                break
            
            if claude.client:
                # Use Claude for parsing
                parsed = claude.parse_liquidation_command(command)
                print(f"🤖 AI parsed: {parsed}")
                # Execute based on parsed result
            else:
                # Use simple regex parsing
                result = agent.execute_command(command)
                print(f"🤖 Result: {result['message']}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            log.error(f"Error: {e}")
    
    print("\nGoodbye! 👋")

if __name__ == "__main__":
    import threading
    main()
