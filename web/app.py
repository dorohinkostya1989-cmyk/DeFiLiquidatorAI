from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import os

from core.config import NETWORK, MIN_PROFIT_USD

app = FastAPI(title="DeFiLiquidatorAI API", description="AI-powered liquidation bot", version="1.0.0")

class LiquidationRequest(BaseModel):
    user_address: str
    network: Optional[str] = "polygon"
    min_profit_usd: Optional[float] = 5.0

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DeFiLiquidatorAI | AI-Powered Liquidation Bot</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0a0f1e 0%, #0d1224 100%);
            min-height: 100vh;
            color: #e2e8f0;
        }

        .glow {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
        }
        
        .glow::before {
            content: '';
            position: absolute;
            top: 20%;
            left: 20%;
            width: 60%;
            height: 60%;
            background: radial-gradient(circle, rgba(79, 172, 254, 0.08) 0%, rgba(79, 172, 254, 0) 70%);
            border-radius: 50%;
        }

        .container {
            position: relative;
            z-index: 1;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }

        /* Header */
        .header {
            text-align: center;
            margin-bottom: 3rem;
        }

        .logo {
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #fff 0%, #4facee 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 1rem;
        }

        .badge-container {
            display: flex;
            justify-content: center;
            gap: 0.75rem;
            flex-wrap: wrap;
            margin-bottom: 1.5rem;
        }

        .badge {
            background: rgba(79, 172, 254, 0.12);
            border: 1px solid rgba(79, 172, 254, 0.3);
            padding: 0.4rem 1rem;
            border-radius: 40px;
            font-size: 0.8rem;
            font-weight: 500;
            backdrop-filter: blur(10px);
        }

        .badge.blue {
            background: #4facee;
            color: #0a0f1e;
            border-color: #4facee;
        }

        .subtitle {
            color: #94a3b8;
            font-size: 1.1rem;
            max-width: 600px;
            margin: 0 auto;
        }

        /* Cards */
        .card {
            background: rgba(18, 25, 45, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(79, 172, 254, 0.15);
            border-radius: 24px;
            padding: 1.75rem;
            transition: all 0.3s ease;
        }

        .card:hover {
            border-color: rgba(79, 172, 254, 0.4);
            box-shadow: 0 8px 32px rgba(79, 172, 254, 0.1);
        }

        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .card-desc {
            color: #94a3b8;
            font-size: 0.85rem;
            margin-bottom: 1.5rem;
        }

        /* Form */
        .form-group {
            margin-bottom: 1.25rem;
        }

        label {
            display: block;
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
            color: #cbd5e1;
        }

        input, select {
            width: 100%;
            padding: 0.85rem 1rem;
            background: rgba(10, 15, 30, 0.8);
            border: 1px solid rgba(79, 172, 254, 0.2);
            border-radius: 16px;
            color: #e2e8f0;
            font-size: 0.9rem;
            font-family: 'Inter', monospace;
            transition: all 0.2s;
        }

        input:focus, select:focus {
            outline: none;
            border-color: #4facee;
            box-shadow: 0 0 0 3px rgba(79, 172, 254, 0.2);
        }

        button {
            width: 100%;
            padding: 0.85rem;
            background: linear-gradient(135deg, #4facee 0%, #3b8fc7 100%);
            border: none;
            border-radius: 16px;
            color: white;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(79, 172, 254, 0.3);
        }

        button:active {
            transform: translateY(0);
        }

        /* Result */
        .result {
            margin-top: 1.5rem;
            padding: 1rem;
            background: rgba(10, 15, 30, 0.6);
            border-radius: 16px;
            border-left: 3px solid #4facee;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.8rem;
            overflow-x: auto;
            white-space: pre-wrap;
            word-break: break-all;
        }

        /* Grid */
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }

        @media (max-width: 768px) {
            .grid-2 {
                grid-template-columns: 1fr;
            }
            .container {
                padding: 1rem;
            }
        }

        /* Status */
        .status {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.25rem 0.75rem;
            background: rgba(34, 197, 94, 0.12);
            border-radius: 40px;
            font-size: 0.75rem;
            color: #4ade80;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: #4ade80;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }

        .footer {
            text-align: center;
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(79, 172, 254, 0.1);
            font-size: 0.75rem;
            color: #475569;
        }
    </style>
</head>
<body>
    <div class="glow"></div>
    <div class="container">
        <div class="header">
            <div class="logo">
                🤖 DeFiLiquidatorAI
            </div>
            <div class="badge-container">
                <span class="badge">⚡ AI-Powered</span>
                <span class="badge">💰 Flash Loans</span>
                <span class="badge">🛡️ Private Mempool</span>
                <span class="badge blue">Open Source</span>
            </div>
            <div class="subtitle">
                Describe the position in plain English — the AI executes the liquidation
            </div>
        </div>

        <div class="grid-2">
            <!-- Liquidate Card -->
            <div class="card">
                <div class="card-title">
                    🔥 Execute Liquidation
                </div>
                <div class="card-desc">
                    Liquidate an underwater Aave position instantly
                </div>
                
                <div class="form-group">
                    <label>Wallet Address</label>
                    <input type="text" id="address" placeholder="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEbA">
                </div>
                
                <div class="form-group">
                    <label>Network</label>
                    <select id="network">
                        <option value="polygon">🟣 Polygon</option>
                        <option value="base">🔵 Base</option>
                        <option value="arbitrum">🔴 Arbitrum</option>
                        <option value="ethereum">⚫ Ethereum</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Min Profit (USD)</label>
                    <input type="number" id="minProfit" value="5.0" step="1">
                </div>
                
                <button onclick="liquidate()">⚡ Execute Liquidation</button>
                
                <div id="result" class="result">
                    <span style="color: #64748b;">Ready. Enter a wallet address to simulate liquidation.</span>
                </div>
            </div>

            <!-- Info Card -->
            <div class="card">
                <div class="card-title">
                    📊 System Status
                </div>
                <div class="card-desc">
                    Real-time monitoring and AI agent status
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <div class="status">
                        <span class="status-dot"></span>
                        API Online
                    </div>
                </div>
                
                <div style="margin-bottom: 1rem;">
                    <div style="background: rgba(79, 172, 254, 0.05); border-radius: 12px; padding: 1rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #94a3b8;">Network</span>
                            <span style="font-weight: 600;">Polygon</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span style="color: #94a3b8;">Min Profit</span>
                            <span style="font-weight: 600;">$5.00</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #94a3b8;">Mode</span>
                            <span style="font-weight: 600;">Simulation</span>
                        </div>
                    </div>
                </div>
                
                <div class="card-title" style="margin-top: 1rem;">
                    🧠 AI Commands
                </div>
                <div class="card-desc">
                    Run in terminal: <code style="background: #0a0f1e; padding: 0.2rem 0.5rem; border-radius: 8px;">python agent_chat.py</code>
                </div>
                <div style="background: rgba(79, 172, 254, 0.05); border-radius: 12px; padding: 1rem; font-family: monospace; font-size: 0.75rem;">
                    > Liquidate 0x742d... on Base if profit > $10<br>
                    > Check 0x742d... on Polygon<br>
                    > Liquidate if profit > $20
                </div>
            </div>
        </div>
        
        <div class="footer">
            DeFiLiquidatorAI • MIT License • AI-Powered Liquidation Bot for Aave v3
        </div>
    </div>

    <script>
    async function liquidate() {
        const address = document.getElementById('address').value;
        const network = document.getElementById('network').value;
        const minProfit = parseFloat(document.getElementById('minProfit').value);
        const resultDiv = document.getElementById('result');
        
        if (!address || !address.startsWith('0x') || address.length !== 42) {
            resultDiv.innerHTML = '<span style="color: #ef4444;">❌ Invalid address. Please enter a valid Ethereum address (0x...)</span>';
            return;
        }
        
        resultDiv.innerHTML = '<span style="color: #4facee;">⏳ Checking position on ' + network + '...</span>';
        
        try {
            const response = await fetch('/api/liquidate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_address: address, network: network, min_profit_usd: minProfit })
            });
            const data = await response.json();
            
            if (data.status === 'simulated') {
                resultDiv.innerHTML = `
                    <span style="color: #4ade80;">✅ Simulation Result</span><br><br>
                    📍 User: ${data.user}<br>
                    🌐 Network: ${data.network}<br>
                    💰 Est. Profit: $${data.estimated_profit}<br>
                    📊 Health Factor: ${data.health_factor}<br><br>
                    <span style="color: #64748b;">⚠️ This is a simulation. In production, this would execute a real transaction.</span>
                `;
            } else {
                resultDiv.innerHTML = '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            }
        } catch(e) {
            resultDiv.innerHTML = '<span style="color: #ef4444;">❌ Error: ' + e.message + '</span>';
        }
    }
    </script>
</body>
</html>
"""


@app.post("/api/liquidate")
async def liquidate(request: LiquidationRequest):
    return {
        "status": "simulated",
        "user": request.user_address,
        "network": request.network,
        "min_profit_usd": request.min_profit_usd,
        "estimated_profit": 45.50,
        "health_factor": 0.97,
        "message": "Liquidation simulation. In production, this would execute the actual transaction."
    }
