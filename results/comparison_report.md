# BTCUSD Strategy Backtest Comparison

- Period: 2025-07-25 to 2026-11-09 (135957 x 5-min candles)
- Starting equity: $10,000 | Risk per trade: 1% of equity
- All strategies use identical trade management: 1:2 target, breakeven at 1R, trail-lock at 1.5R

| Strategy | Trades | Win Rate | Profit Factor | Total Return | Max Drawdown | Avg R |
|---|---|---|---|---|---|---|
| Current Strategy (close-vs-EMA IB/Marubozu + swing HH/LL) | 4823 | 39.4% | 1.16 | 3729.1% | 20.3% | 0.08 |
| EMA 9/21 Crossover (trend-following baseline) | 1970 | 33.8% | 0.89 | -62.4% | 67.2% | -0.04 |
| Donchian Channel Breakout (20-period) | 586 | 32.9% | 0.92 | -20.2% | 32.8% | -0.03 |

**Best total return over this period: Current Strategy (close-vs-EMA IB/Marubozu + swing HH/LL)** (3729.1%)

_Note: past performance on historical data doesn't guarantee future results. Check trade counts before trusting a metric — a strategy with very few trades can show a misleadingly extreme win rate or return._
