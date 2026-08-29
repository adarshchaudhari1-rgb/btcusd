"""
Alternate strategy #1: simple 9/21 EMA crossover, trend-following.
Long when 9 EMA crosses above 21 EMA; short when it crosses below.
SL: recent swing low/high (last 5 candles); Target 1:2 (buffer/trailing
handled by the shared engine, same as the current strategy, for a fair
apples-to-apples comparison).
"""
from .common import ema_series

FAST, SLOW = 9, 21
SL_BUFFER_PCT = 0.0005
SWING_LOOKBACK = 5

NAME = "EMA 9/21 Crossover (trend-following baseline)"


def generate_signals(candles):
    closes = [c["close"] for c in candles]
    fast = ema_series(closes, FAST)
    slow = ema_series(closes, SLOW)

    signals = {}
    n = len(candles)
    for i in range(SLOW + SWING_LOOKBACK + 1, n - 1):
        if fast[i - 1] is None or slow[i - 1] is None or fast[i] is None or slow[i] is None:
            continue
        crossed_up = fast[i - 1] <= slow[i - 1] and fast[i] > slow[i]
        crossed_down = fast[i - 1] >= slow[i - 1] and fast[i] < slow[i]
        if not (crossed_up or crossed_down):
            continue

        window = candles[i - SWING_LOOKBACK:i + 1]
        direction = "long" if crossed_up else "short"
        sl_raw = min(c["low"] for c in window) if direction == "long" else max(c["high"] for c in window)

        signals[i + 1] = {
            "direction": direction,
            "trigger_high": candles[i]["high"],
            "trigger_low": candles[i]["low"],
            "sl_raw": sl_raw,
            "sl_buffer_pct": SL_BUFFER_PCT,
            "immediate_entry": True,  # enter at next candle's open, no breakout needed
        }
    return signals

