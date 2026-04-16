from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import os

from core.config import NETWORK, MIN_PROFIT_USD
from core.helpers import estimate_profit, parse_health_factor

app = FastAPI(title="DeFiLiquidatorAI API", description="AI-powered liquidation bot", version="1.0.0")

class LiquidationRequest(BaseModel):
    user_address: str
    network: Optional[str] = "polygon"
    min_profit_usd: Optional[float] = 5.0

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DeFiLiquidatorAI</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #0a0a0a; color: #fff; }
            .container { max-width: 800px; margin: auto; background: #1a1a1a; padding: 20px; border-radius: 10px; }
            input, button { padding: 10px; margin: 5px; width: 100%; }
            button { background: #4CAF50; color: white; border: none; cursor: pointer; }
            .result { margin-top: 20px; padding: 10px; background: #2a2a2a; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 DeFiLiquidatorAI</h1>
            <p>AI-powered liquidation bot for Aave v3</p>
            
            <h3>Liquidate Position</h3>
            <input type="text" id="address" placeholder="User address (0x...)" />
            <select id="network">
                <option value="polygon">Polygon</option>
                <option value="base">Base</option>
                <option value="arbitrum">Arbitrum</option>
                <option value="ethereum">Ethereum</option>
            </select>
            <input type="number" id="minProfit" placeholder="Min profit USD" value="5.0" />
            <button onclick="liquidate()">Execute Liquidation</button>
            <div id="result" class="result"></div>
        </div>
        
        <script>
        async function liquidate() {
            const address = document.getElementById('address').value;
            const network = document.getElementById('network').value;
            const minProfit = parseFloat(document.getElementById('minProfit').value);
            const resultDiv = document.getElementById('result');
            
            resultDiv.innerHTML = "⏳ Checking position...";
            
            try {
                const response = await fetch('/api/liquidate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_address: address, network: network, min_profit_usd: minProfit })
                });
                const data = await response.json();
                resultDiv.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            } catch(e) {
                resultDiv.innerHTML = "❌ Error: " + e.message;
            }
        }
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health():
    return {"status": "ok", "network": NETWORK, "min_profit_usd": MIN_PROFIT_USD}

@app.post("/api/liquidate")
async def liquidate(request: LiquidationRequest):
    # This is a mock response - actual liquidation would call the smart contract
    return {
        "status": "simulated",
        "user": request.user_address,
        "network": request.network,
        "min_profit_usd": request.min_profit_usd,
        "message": "Liquidation simulation. In production, this would execute the actual transaction.",
        "estimated_profit": 45.50,
        "health_factor": 0.97
    }
