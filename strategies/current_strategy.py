"""
Your current refined strategy:
- Trend: real swing-structure HH/LL (fractal swings), not raw EMA slope.
  Only trades with a confirmed uptrend (HH+HL) or downtrend (LH+LL); skips
  choppy/sideways periods entirely.
- EMA filter (simplified, no touch/tolerance): candle CLOSE above the 9 EMA
  for buy-side setups, candle CLOSE below the 9 EMA for sell-side setups.
- Setup A (Inside Bar): mother candle closes on the correct side of the EMA,
  and the inside (baby) candle forms within its range.
- Setup B (Marubozu): one of three variants -
    close=high (bull_close_high), close=low (bear_close_low), or classic
    full marubozu (negligible wicks both ends) - with its close on the
    correct side of the EMA.
- Entry: breakout of the setup candle's high/low on the next candle.
- SL: just beyond that candle's low/high (small % buffer).
- Target: 1:2 risk-reward.
- Trailing SL: breakeven at 1R, then trail to lock 1R profit once price
  reaches 1.5R (handled by the shared backtest engine, not here).
"""
from .common import ema_series, find_fractal_swings, trend_as_of, is_inside_bar, marubozu_variant

EMA_PERIOD = 9
SL_BUFFER_PCT = 0.0005

NAME = "Current Strategy (close-vs-EMA IB/Marubozu + swing HH/LL)"


def generate_signals(candles):
    """Returns dict: index -> signal dict, for the candle at which entry should be evaluated."""
    closes = [c["close"] for c in candles]
    emas = ema_series(closes, EMA_PERIOD)
    swing_highs, swing_lows = find_fractal_swings(candles, arm=2)

    signals = {}
    n = len(candles)
    for i in range(EMA_PERIOD + 5, n - 1):
        trend = trend_as_of(swing_highs, swing_lows, i)
        if trend is None:
            continue

        setup_candle = None
        direction = None

        mother, baby = candles[i - 1], candles[i]
        ema_mother, ema_baby = emas[i - 1], emas[i]
        if ema_mother is None or ema_baby is None:
            continue

        # Setup A: inside bar, mother's close on the correct side of the EMA
        if is_inside_bar(mother, baby):
            if trend == "up" and mother["close"] > ema_mother:
                setup_candle, direction = mother, "long"
            elif trend == "down" and mother["close"] < ema_mother:
                setup_candle, direction = mother, "short"

        # Setup B: marubozu, close on the correct side of the EMA
        if setup_candle is None:
            variant = marubozu_variant(baby)
            if variant:
                if variant in ("bull_full", "bull_close_high") and trend == "up" and baby["close"] > ema_baby:
                    setup_candle, direction = baby, "long"
                elif variant in ("bear_full", "bear_close_low") and trend == "down" and baby["close"] < ema_baby:
                    setup_candle, direction = baby, "short"

        if setup_candle is None:
            continue

        entry_level_high = setup_candle["high"]
        entry_level_low = setup_candle["low"]

        signals[i + 1] = {
            "direction": direction,
            "trigger_high": entry_level_high,
            "trigger_low": entry_level_low,
            "sl_raw": entry_level_low if direction == "long" else entry_level_high,
            "sl_buffer_pct": SL_BUFFER_PCT,
        }
    return signals
