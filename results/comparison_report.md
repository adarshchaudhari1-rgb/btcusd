# BTCUSD Strategy Backtest Comparison

- Period: 2025-07-25 to 2026-10-19 (129879 x 5-min candles)
- Starting equity: $10,000 | Risk per trade: 1% of equity
- All strategies use identical trade management: 1:2 target, breakeven at 1R, trail-lock at 1.5R

| Strategy | Trades | Win Rate | Profit Factor | Total Return | Max Drawdown | Avg R |
|---|---|---|---|---|---|---|
| Current Strategy (close-vs-EMA IB/Marubozu + swing HH/LL) | 4623 | 39.6% | 1.21 | 4051.4% | 20.3% | 0.09 |
| EMA 9/21 Crossover (trend-following baseline) | 1881 | 34.1% | 0.9 | -55.7% | 64.5% | -0.04 |
| Donchian Channel Breakout (20-period) | 564 | 32.6% | 0.9 | -22.5% | 32.8% | -0.04 |

**Best total return over this period: Current Strategy (close-vs-EMA IB/Marubozu + swing HH/LL)** (4051.4%)

_Note: past performance on historical data doesn't guarantee future results. Check trade counts before trusting a metric — a strategy with very few trades can show a misleadingly extreme win rate or return._
