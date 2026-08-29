"""
Alternate strategy #2: Donchian channel breakout.
Long when close breaks above the highest high of the prior N candles;
short when close breaks below the lowest low of the prior N candles.
SL: opposite band value at breakout time; Target 1:2 (buffer/trailing
handled by the shared engine).
"""
N = 20
SL_BUFFER_PCT = 0.0005

NAME = f"Donchian Channel Breakout ({N}-period)"


def generate_signals(candles):
    signals = {}
    n = len(candles)
    for i in range(N + 1, n - 1):
        window = candles[i - N:i]
        highest = max(c["high"] for c in window)
        lowest = min(c["low"] for c in window)
        close = candles[i]["close"]

        direction = None
        if close > highest:
            direction = "long"
        elif close < lowest:
            direction = "short"
        if direction is None:
            continue

        sl_raw = lowest if direction == "long" else highest

        signals[i + 1] = {
            "direction": direction,
            "trigger_high": candles[i]["high"],
            "trigger_low": candles[i]["low"],
            "sl_raw": sl_raw,
            "sl_buffer_pct": SL_BUFFER_PCT,
            "immediate_entry": True,
        }
    return signals
