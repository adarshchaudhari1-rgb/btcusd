"""
Shared trade-management engine. Every strategy only proposes setups
(direction, breakout trigger levels, raw SL); this engine handles entry
confirmation, SL buffer, 1:2 target, and the breakeven/trail-lock rules
identically for every strategy, so comparisons are apples-to-apples.

Rules (same as your NSE bot):
- One open position at a time; new signals are ignored while in a trade.
- Entry: breakout of the trigger candle's high/low (unless the strategy
  marks `immediate_entry`, in which case it enters at the next candle's open).
- SL: raw level +/- a small % buffer.
- Target: 1:2 risk-reward.
- Trailing: move SL to breakeven at 1R; once price reaches 1.5R, trail SL to
  lock in 1R of profit.
"""
RISK_REWARD = 2.0
BREAKEVEN_AT_R = 1.0
TRAIL_LOCK_AT_R = 1.5


def run_backtest(candles, signals, starting_equity=10000.0, risk_pct=0.01):
    """
    candles: list of OHLC dicts (time, open, high, low, close)
    signals: dict index -> setup dict from a strategy's generate_signals()
    Returns (trades: list[dict], equity_curve: list[float])
    """
    trades = []
    equity = starting_equity
    equity_curve = [equity]
    open_pos = None
    pending = None  # a signal waiting for breakout confirmation

    n = len(candles)
    for i in range(n):
        candle = candles[i]

        # 1. Manage open position first
        if open_pos:
            direction = open_pos["direction"]
            entry = open_pos["entry"]
            risk = open_pos["risk"]
            sl = open_pos["sl"]
            target = open_pos["target"]

            # use intrabar high/low for realistic SL/target touches
            hit_target = candle["high"] >= target if direction == "long" else candle["low"] <= target
            hit_sl = candle["low"] <= sl if direction == "long" else candle["high"] >= sl

            # trailing updates based on the candle's favorable extreme
            fav_price = candle["high"] if direction == "long" else candle["low"]
            r_multiple = (fav_price - entry) / risk if direction == "long" else (entry - fav_price) / risk

            if r_multiple >= TRAIL_LOCK_AT_R and not open_pos["trailed"]:
                open_pos["sl"] = entry + risk if direction == "long" else entry - risk
                open_pos["trailed"] = True
                sl = open_pos["sl"]
                hit_sl = candle["low"] <= sl if direction == "long" else candle["high"] >= sl
            elif r_multiple >= BREAKEVEN_AT_R and not open_pos["breakeven"]:
                open_pos["sl"] = entry
                open_pos["breakeven"] = True
                sl = open_pos["sl"]
                hit_sl = candle["low"] <= sl if direction == "long" else candle["high"] >= sl

            exit_price, exit_reason = None, None
            # if both hit in the same candle, assume SL first (conservative)
            if hit_sl:
                exit_price, exit_reason = sl, "SL"
            elif hit_target:
                exit_price, exit_reason = target, "Target"

            if exit_price is not None:
                pnl_r = (exit_price - entry) / risk if direction == "long" else (entry - exit_price) / risk
                dollar_risk = equity * risk_pct
                pnl_dollars = pnl_r * dollar_risk
                equity += pnl_dollars
                trades.append({
                    "entry_time": open_pos["entry_time"], "exit_time": candle["time"],
                    "direction": direction, "entry": entry, "exit": exit_price,
                    "sl": open_pos["orig_sl"], "target": target, "exit_reason": exit_reason,
                    "pnl_r": round(pnl_r, 2), "pnl_dollars": round(pnl_dollars, 2),
                    "equity_after": round(equity, 2),
                })
                open_pos = None

        # 2. Check pending breakout confirmation
        if pending and open_pos is None:
            sig = pending
            triggered, entry_price = False, None
            if sig.get("immediate_entry"):
                triggered, entry_price = True, candle["open"]
            else:
                if sig["direction"] == "long" and candle["high"] > sig["trigger_high"]:
                    triggered, entry_price = True, sig["trigger_high"]
                elif sig["direction"] == "short" and candle["low"] < sig["trigger_low"]:
                    triggered, entry_price = True, sig["trigger_low"]

            if triggered:
                sl_raw = sig["sl_raw"]
                buf = sig["sl_buffer_pct"]
                sl = sl_raw * (1 - buf) if sig["direction"] == "long" else sl_raw * (1 + buf)
                risk = abs(entry_price - sl)
                if risk > 0:
                    target = entry_price + risk * RISK_REWARD if sig["direction"] == "long" else entry_price - risk * RISK_REWARD
                    open_pos = {
                        "direction": sig["direction"], "entry": entry_price, "sl": sl, "orig_sl": sl,
                        "target": target, "risk": risk, "entry_time": candle["time"],
                        "breakeven": False, "trailed": False,
                    }
            pending = None  # signal consumed (triggered or expired) after one candle

        # 3. Pick up new signal for this index (only if flat and nothing pending)
        if i in signals and open_pos is None and pending is None:
            pending = signals[i]

        equity_curve.append(equity)

    return trades, equity_curve


def compute_metrics(trades, equity_curve, starting_equity=10000.0):
    if not trades:
        return {
            "total_trades": 0, "win_rate": 0, "profit_factor": 0,
            "total_return_pct": 0, "max_drawdown_pct": 0, "avg_r": 0, "expectancy_r": 0,
        }
    wins = [t for t in trades if t["pnl_dollars"] > 0]
    losses = [t for t in trades if t["pnl_dollars"] <= 0]
    gross_profit = sum(t["pnl_dollars"] for t in wins)
    gross_loss = abs(sum(t["pnl_dollars"] for t in losses))
    final_equity = equity_curve[-1]

    peak = equity_curve[0]
    max_dd = 0
    for e in equity_curve:
        peak = max(peak, e)
        dd = (peak - e) / peak * 100 if peak > 0 else 0
        max_dd = max(max_dd, dd)

    avg_r = sum(t["pnl_r"] for t in trades) / len(trades)

    return {
        "total_trades": len(trades),
        "wins": len(wins),
        "losses": len(losses),
        "win_rate": round(len(wins) / len(trades) * 100, 1),
        "profit_factor": round(gross_profit / gross_loss, 2) if gross_loss > 0 else float("inf"),
        "total_return_pct": round((final_equity - starting_equity) / starting_equity * 100, 1),
        "max_drawdown_pct": round(max_dd, 1),
        "avg_r": round(avg_r, 2),
        "expectancy_r": round(avg_r, 2),
        "final_equity": round(final_equity, 2),
    }
