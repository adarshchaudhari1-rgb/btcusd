"""Shared indicators and candle-pattern helpers for all strategies."""


def ema_series(closes, period):
    k = 2 / (period + 1)
    out = [None] * len(closes)
    if len(closes) < period:
        return out
    sma = sum(closes[:period]) / period
    out[period - 1] = sma
    prev = sma
    for i in range(period, len(closes)):
        prev = closes[i] * k + prev * (1 - k)
        out[i] = prev
    return out


def find_fractal_swings(candles, arm=2):
    """
    5-bar fractal swing points (2 candles on each side).
    Returns two lists of (index, price): swing_highs, swing_lows.
    A swing is only 'confirmed' once `arm` candles after it exist, so it's
    safe to use causally once you're arm candles past it.
    """
    swing_highs, swing_lows = [], []
    n = len(candles)
    for i in range(arm, n - arm):
        window = candles[i - arm:i + arm + 1]
        h = candles[i]["high"]
        l = candles[i]["low"]
        if h == max(c["high"] for c in window):
            swing_highs.append((i, h))
        if l == min(c["low"] for c in window):
            swing_lows.append((i, l))
    return swing_highs, swing_lows


def trend_as_of(swing_highs, swing_lows, idx, arm=2):
    """
    'up' if the last two confirmed swing highs AND last two confirmed swing
    lows (both fully before idx) are each rising; 'down' if both falling;
    None otherwise (choppy / no clear structure -> skip trading).
    A swing at index i is only usable once idx > i + arm, since that's when
    it becomes knowable in real time (it takes `arm` candles after the swing
    to confirm it as a swing at all).
    """
    highs = [p for i, p in swing_highs if idx > i + arm]
    lows = [p for i, p in swing_lows if idx > i + arm]
    if len(highs) < 2 or len(lows) < 2:
        return None
    hh = highs[-1] > highs[-2]
    hl = lows[-1] > lows[-2]
    lh = highs[-1] < highs[-2]
    ll = lows[-1] < lows[-2]
    if hh and hl:
        return "up"
    if lh and ll:
        return "down"
    return None


def touches_ema(candle, ema_val):
    if ema_val is None:
        return False
    return candle["low"] <= ema_val <= candle["high"]


def is_inside_bar(mother, baby):
    return baby["high"] <= mother["high"] and baby["low"] >= mother["low"]


def marubozu_variant(candle, wick_tol=0.08):
    """
    Returns 'bull_full', 'bull_close_high', 'bear_full', 'bear_close_low', or None.
    wick_tol: max wick size as a fraction of the candle's range to still count
    as 'touching' that extreme (close/open effectively AT the high/low).
    """
    o, h, l, c = candle["open"], candle["high"], candle["low"], candle["close"]
    rng = h - l
    if rng <= 0:
        return None
    upper_wick = (h - max(o, c)) / rng
    lower_wick = (min(o, c) - l) / rng
    bullish = c > o
    bearish = c < o

    if bullish and upper_wick <= wick_tol and lower_wick <= wick_tol:
        return "bull_full"
    if bearish and upper_wick <= wick_tol and lower_wick <= wick_tol:
        return "bear_full"
    if bullish and upper_wick <= wick_tol:
        return "bull_close_high"
    if bearish and lower_wick <= wick_tol:
        return "bear_close_low"
    return None
