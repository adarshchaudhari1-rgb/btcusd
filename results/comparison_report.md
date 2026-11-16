# BTCUSD Strategy Backtest Comparison

- Period: 2025-07-25 to 2026-11-16 (137969 x 5-min candles)
- Starting equity: $10,000 | Risk per trade: 1% of equity
- All strategies use identical trade management: 1:2 target, breakeven at 1R, trail-lock at 1.5R

| Strategy | Trades | Win Rate | Profit Factor | Total Return | Max Drawdown | Avg R |
|---|---|---|---|---|---|---|
| Current Strategy (close-vs-EMA IB/Marubozu + swing HH/LL) | 4887 | 39.4% | 1.17 | 4115.4% | 20.3% | 0.08 |
| EMA 9/21 Crossover (trend-following baseline) | 1990 | 33.8% | 0.88 | -64.7% | 69.2% | -0.05 |
| Donchian Channel Breakout (20-period) | 591 | 33.3% | 0.94 | -14.5% | 32.8% | -0.02 |

**Best total return over this period: Current Strategy (close-vs-EMA IB/Marubozu + swing HH/LL)** (4115.4%)

_Note: past performance on historical data doesn't guarantee future results. Check trade counts before trusting a metric — a strategy with very few trades can show a misleadingly extreme win rate or return._
