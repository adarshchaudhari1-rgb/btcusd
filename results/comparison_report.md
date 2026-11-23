# BTCUSD Strategy Backtest Comparison

- Period: 2025-07-25 to 2026-11-23 (139999 x 5-min candles)
- Starting equity: $10,000 | Risk per trade: 1% of equity
- All strategies use identical trade management: 1:2 target, breakeven at 1R, trail-lock at 1.5R

| Strategy | Trades | Win Rate | Profit Factor | Total Return | Max Drawdown | Avg R |
|---|---|---|---|---|---|---|
| Current Strategy (close-vs-EMA IB/Marubozu + swing HH/LL) | 4950 | 39.5% | 1.19 | 4681.8% | 20.3% | 0.08 |
| EMA 9/21 Crossover (trend-following baseline) | 2000 | 33.9% | 0.89 | -64.3% | 69.5% | -0.05 |
| Donchian Channel Breakout (20-period) | 594 | 33.5% | 0.95 | -12.8% | 32.8% | -0.02 |

**Best total return over this period: Current Strategy (close-vs-EMA IB/Marubozu + swing HH/LL)** (4681.8%)

_Note: past performance on historical data doesn't guarantee future results. Check trade counts before trusting a metric — a strategy with very few trades can show a misleadingly extreme win rate or return._
