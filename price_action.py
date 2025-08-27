import pandas as pd
from config import S_R_WINDOW, VOL_SPIKE_MULT

def recent_hh_ll(df: pd.DataFrame, window: int = S_R_WINDOW):
    hh = df["high"].rolling(window).max()
    ll = df["low"].rolling(window).min()
    return hh, ll

def is_breakout(last_close: float, last_hh: float, vol_spike: bool = False, bb_upper: float = None) -> bool:
    cond = (last_close > last_hh) or (bb_upper is not None and last_close > bb_upper and vol_spike)
    return bool(cond)

def is_breakdown(last_close: float, last_ll: float, vol_spike: bool = False, bb_lower: float = None) -> bool:
    cond = (last_close < last_ll) or (bb_lower is not None and last_close < bb_lower and vol_spike)
    return bool(cond)

def near_support(last_close: float, recent_low: float, atr_val: float, mult: float = 1.0) -> bool:
    return (last_close - recent_low) <= mult * atr_val

def near_resistance(last_close: float, recent_high: float, atr_val: float, mult: float = 1.0) -> bool:
    return (recent_high - last_close) <= mult * atr_val

def candle_patterns(df: pd.DataFrame) -> list:
    o, h, l, c = df["open"].iloc[-1], df["high"].iloc[-1], df["low"].iloc[-1], df["close"].iloc[-1]
    o1, c1 = df["open"].iloc[-2], df["close"].iloc[-2]
    body = abs(c - o)
    full = max(h - l, 1e-9)
    upper_wick = h - max(c, o)
    lower_wick = min(c, o) - l

    patterns = []
    if (c1 < o1) and (c > o) and (c >= o1) and (o <= c1):
        patterns.append("BullishEngulfing")
    if (c1 > o1) and (c < o) and (o >= c1) and (c <= o1):
        patterns.append("BearishEngulfing")
    if lower_wick > 2 * body and upper_wick < body and c > o:
        patterns.append("Hammer")
    if upper_wick > 2 * body and lower_wick < body and c < o:
        patterns.append("ShootingStar")
    if body / full < 0.1:
        patterns.append("Doji")
    return patterns