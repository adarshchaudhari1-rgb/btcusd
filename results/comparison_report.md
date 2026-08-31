# BTCUSD Strategy Backtest Comparison

- Period: 2025-07-25 to 2026-08-31 (115701 x 5-min candles)
- Starting equity: $10,000 | Risk per trade: 1% of equity
- All strategies use identical trade management: 1:2 target, breakeven at 1R, trail-lock at 1.5R

| Strategy | Trades | Win Rate | Profit Factor | Total Return | Max Drawdown | Avg R |
|---|---|---|---|---|---|---|
| Current Strategy (close-vs-EMA IB/Marubozu + swing HH/LL) | 4119 | 39.6% | 1.2 | 2516.3% | 20.3% | 0.08 |
| EMA 9/21 Crossover (trend-following baseline) | 1706 | 34.5% | 0.91 | -44.3% | 64.5% | -0.03 |
| Donchian Channel Breakout (20-period) | 508 | 32.7% | 0.9 | -20.6% | 32.8% | -0.04 |

**Best total return over this period: Current Strategy (close-vs-EMA IB/Marubozu + swing HH/LL)** (2516.3%)

_Note: past performance on historical data doesn't guarantee future results. Check trade counts before trusting a metric — a strategy with very few trades can show a misleadingly extreme win rate or return._
