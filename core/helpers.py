"""
Helper functions for health factor, profit calculation, and gas analysis
"""

def get_close_factor(debt_usd: float, collateral_usd: float, hf: float) -> float:
    if hf < 0.95:
        return 1.0
    if debt_usd < 2000 or collateral_usd < 2000:
        return 1.0
    return 0.5

def estimate_profit(debt_usd: float, bonus_pct: float = 0.05, gas_usd: float = 0.10) -> float:
    if debt_usd <= 0:
        return 0.0
    cover_amount = debt_usd * 0.5
    gross_profit = cover_amount * bonus_pct
    net_profit = gross_profit - gas_usd - 0.05
    return max(0, net_profit)

def parse_health_factor(raw_hf: int) -> float:
    return raw_hf / 1e18

def parse_debt(raw_debt: int) -> float:
    return raw_debt / 1e8
