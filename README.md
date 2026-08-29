# BTCUSD Strategy Backtest — Comparison

Backtests **your refined strategy** against two simple alternates on 400+
days of real BTCUSD 5-minute candles from Delta Exchange's public API, using
identical trade management for all three so the comparison is fair.

## Strategies tested

1. **Current Strategy** (`strategies/current_strategy.py`) — your latest rules:
   - Trend filter: confirmed swing-structure HH/HL (up) or LH/LL (down) using
     5-bar fractals — skips choppy periods with no clear structure.
   - Inside Bar setup: mother candle must touch the 9 EMA.
   - Marubozu setup: three variants (close=high, close=low, classic full
     marubozu with negligible wicks), and it must touch the 9 EMA.
   - Entry on breakout of the setup candle's range.
2. **EMA 9/21 Crossover** (`strategies/ema_cross_strategy.py`) — a plain
   trend-following baseline, enters immediately on crossover, SL at the
   recent 5-candle swing.
3. **Donchian Channel Breakout** (`strategies/donchian_breakout_strategy.py`)
   — enters on a 20-period high/low breakout, a classic simple breakout
   system.

All three use the **same exit rules** (from the shared engine in
`backtest_engine.py`), matching your NSE bot: SL just beyond the setup range
(0.05% buffer), 1:2 target, move to breakeven at 1R, trail to lock 1R once
price reaches 1.5R. Position sizing: 1% of equity risked per trade,
starting from a $10,000 paper account.

## How it runs

Everything runs automatically via GitHub Actions (`.github/workflows/backtest.yml`):

- **Weekly** (Monday 03:00 UTC) — or trigger manually anytime from the
  Actions tab ("Run workflow").
- `fetch_data.py` pulls 400 days of 5m candles from Delta's public API,
  paginated in 3-day chunks, and **resumes** from the last saved timestamp
  on every run (so it only fetches new candles after the first run).
- `run_backtest.py` runs all three strategies through the shared engine and
  writes `results/comparison_report.md` — a table with trades, win rate,
  profit factor, total return, max drawdown, and average R for each.
- Per-strategy trade logs are saved to `results/trades_<strategy>.csv` if
  you want to dig into individual trades.
- Data (`data/btcusd_5m.csv`) and results are committed back to the repo
  each run, so you just open `results/comparison_report.md` to see the
  latest numbers — no need to run anything locally.

## Important caveats

- **This is real historical price data, but a simplified paper-trade
  simulation** — no slippage, funding fees, or partial fills modeled. Real
  paper/live trading (like your GitHub-Actions BTCUSD agent) will differ.
- Check the **trade count** before trusting any single metric — a strategy
  with very few trades can show a misleadingly extreme win rate or return
  just from small-sample luck.
- A backtest showing a strategy "wins" doesn't guarantee it keeps working —
  markets change regime. Treat this as a starting filter, not a green light
  to go live.
- I couldn't run this backtest myself before handing it to you — my sandbox
  can't reach Delta Exchange's API directly, so this is untested against
  real BTC data (it was smoke-tested against synthetic random-walk data to
  confirm there are no code errors, but real results will look different).
  Check the first automated run's output carefully.
