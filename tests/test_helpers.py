import sys
sys.path.append('.')
from core.helpers import estimate_profit, parse_health_factor

def test_estimate_profit():
    profit = estimate_profit(1000)
    assert profit > 0
    print("✅ Profit test passed")

def test_parse_health_factor():
    hf = parse_health_factor(1000000000000000000)
    assert hf == 1.0
    print("✅ Health factor test passed")

if __name__ == "__main__":
    test_estimate_profit()
    test_parse_health_factor()
    print("\n🎉 All tests passed!")
