import csv
import os
from datetime import datetime, timezone

from backtest_engine import run_backtest, compute_metrics
from strategies import current_strategy, ema_cross_strategy, donchian_breakout_strategy

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "btcusd_5m.csv")
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
STARTING_EQUITY = 10000.0
RISK_PCT = 0.01  # 1% of equity risked per trade

STRATEGIES = [current_strategy, ema_cross_strategy, donchian_breakout_strategy]


def load_candles():
    candles = []
    with open(DATA_FILE) as f:
        reader = csv.DictReader(f)
        for row in reader:
            candles.append({
                "time": int(row["time"]),
                "open": float(row["open"]), "high": float(row["high"]),
                "low": float(row["low"]), "close": float(row["close"]),
                "volume": float(row.get("volume", 0)),
            })
    candles.sort(key=lambda c: c["time"])
    return candles


def main():
    if not os.path.exists(DATA_FILE):
        raise SystemExit(f"No data found at {DATA_FILE}. Run fetch_data.py first.")

    candles = load_candles()
    if len(candles) < 500:
        raise SystemExit(f"Only {len(candles)} candles loaded — need more history. Run fetch_data.py.")

    start_date = datetime.fromtimestamp(candles[0]["time"], tz=timezone.utc).date()
    end_date = datetime.fromtimestamp(candles[-1]["time"], tz=timezone.utc).date()
    print(f"Loaded {len(candles)} candles: {start_date} -> {end_date}")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    all_results = []

    for strat in STRATEGIES:
        print(f"\nRunning: {strat.NAME}")
        signals = strat.generate_signals(candles)
        trades, equity_curve = run_backtest(candles, signals, STARTING_EQUITY, RISK_PCT)
        metrics = compute_metrics(trades, equity_curve, STARTING_EQUITY)
        print(f"  {metrics}")
        all_results.append({"name": strat.NAME, "metrics": metrics, "trades": trades})

        # per-strategy trade log
        slug = strat.__name__.split(".")[-1]
        trade_csv = os.path.join(RESULTS_DIR, f"trades_{slug}.csv")
        if trades:
            with open(trade_csv, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=list(trades[0].keys()))
                writer.writeheader()
                writer.writerows(trades)

    write_report(all_results, start_date, end_date, len(candles))


def write_report(all_results, start_date, end_date, n_candles):
    path = os.path.join(RESULTS_DIR, "comparison_report.md")
    with open(path, "w") as f:
        f.write("# BTCUSD Strategy Backtest Comparison\n\n")
        f.write(f"- Period: {start_date} to {end_date} ({n_candles} x 5-min candles)\n")
        f.write(f"- Starting equity: ${STARTING_EQUITY:,.0f} | Risk per trade: {RISK_PCT*100:.0f}% of equity\n")
        f.write(f"- All strategies use identical trade management: 1:2 target, "
                f"breakeven at 1R, trail-lock at 1.5R\n\n")
        f.write("| Strategy | Trades | Win Rate | Profit Factor | Total Return | Max Drawdown | Avg R |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for r in all_results:
            m = r["metrics"]
            f.write(f"| {r['name']} | {m['total_trades']} | {m.get('win_rate',0)}% | "
                    f"{m.get('profit_factor',0)} | {m.get('total_return_pct',0)}% | "
                    f"{m.get('max_drawdown_pct',0)}% | {m.get('avg_r',0)} |\n")

        best = max(all_results, key=lambda r: r["metrics"].get("total_return_pct", -999))
        f.write(f"\n**Best total return over this period: {best['name']}** "
                f"({best['metrics'].get('total_return_pct',0)}%)\n")
        f.write("\n_Note: past performance on historical data doesn't guarantee future results. "
                "Check trade counts before trusting a metric — a strategy with very few trades "
                "can show a misleadingly extreme win rate or return._\n")

    print(f"\nReport written: {path}")


if __name__ == "__main__":
    main()
