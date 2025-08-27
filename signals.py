import pandas as pd
import numpy as np
from config import S_R_WINDOW, USE_ATR_SL, ATR_MULT, RISK_PER_TRADE, RR_TP1, RR_TP2, TIMEFRAME, VOL_SPIKE_MULT
from indicators import ema, rsi, macd, atr, bollinger
from price_action import recent_hh_ll, is_breakout, is_breakdown, near_support, near_resistance, candle_patterns
from data import fetch_balance_usdt

def build_features(df: pd.DataFrame, exchange) -> pd.DataFrame:
    out = df.copy()
    out["ema20"] = ema(out["close"], 20)
    out["ema50"] = ema(out["close"], 50)
    out["ema200"] = ema(out["close"], 200)
    out["rsi14"] = rsi(out["close"], 14)
    out["macd"], out["macd_signal"], out["macd_hist"] = macd(out["close"])
    out["atr14"] = atr(out, 14)
    out["bb_upper"], out["bb_mid"], out["bb_lower"] = bollinger(out["close"], 20, 2.0)
    out["vol_sma20"] = out["volume"].rolling(20).mean()
    out["hh20"], out["ll20"] = recent_hh_ll(out, S_R_WINDOW)
    return out

def generate_signal_row(df_feat: pd.DataFrame, exchange,SYMBOL: str) -> dict:
    if len(df_feat) < max(200, S_R_WINDOW + 5):
        return None

    row = df_feat.iloc[-2]
    patterns = candle_patterns(df_feat.iloc[:-1])
    vol_spike = (row["volume"] > VOL_SPIKE_MULT * (row["vol_sma20"] or np.nan)) if not np.isnan(row["vol_sma20"]) else False

    trend_bull = (row["close"] > row["ema50"]) and (row["ema50"] > row["ema200"])
    trend_bear = (row["close"] < row["ema50"]) and (row["ema50"] < row["ema200"])
    macd_bull = row["macd"] > row["macd_signal"] and row["macd_hist"] > 0
    macd_bear = row["macd"] < row["macd_signal"] and row["macd_hist"] < 0
    rsi_bull = 50 <= row["rsi14"] <= 70
    rsi_bear = 30 <= row["rsi14"] <= 50

    breakout_up = is_breakout(row["close"], row["hh20"], vol_spike=vol_spike, bb_upper=row["bb_upper"])
    breakdown = is_breakdown(row["close"], row["ll20"], vol_spike=vol_spike, bb_lower=row["bb_lower"])

    bull_score = sum([trend_bull, macd_bull, rsi_bull, breakout_up])
    bear_score = sum([trend_bear, macd_bear, rsi_bear, breakdown])

    if "BullishEngulfing" in patterns or "Hammer" in patterns:
        bull_score += 2 if near_support(row["close"], row["ll20"], row["atr14"]) else 1
    if "BearishEngulfing" in patterns or "ShootingStar" in patterns:
        bear_score += 2 if near_resistance(row["close"], row["hh20"], row["atr14"]) else 1

    decision = "WAIT"
    reason = [f"bull_score={bull_score}", f"bear_score={bear_score}"]
    if bull_score >= 3 and bull_score >= bear_score + 1:
        decision = "BUY"
    elif bear_score >= 3 and bear_score >= bear_score + 1:
        decision = "SELL"

    entry = float(row["close"])
    atr_val = float(row["atr14"]) if not np.isnan(row["atr14"]) else None
    recent_high = float(row["hh20"])
    recent_low = float(row["ll20"])

    stop = None
    if decision == "BUY":
        stop = entry - ATR_MULT * atr_val if USE_ATR_SL and atr_val else recent_low
    elif decision == "SELL":
        stop = entry + ATR_MULT * atr_val if USE_ATR_SL and atr_val else recent_high

    balance = fetch_balance_usdt(exchange)
    risk_amount = balance * RISK_PER_TRADE
    risk_per_unit = abs(entry - stop) if stop else None
    qty = risk_amount / risk_per_unit if risk_per_unit and risk_per_unit > 0 else None
    if qty:
        qty = float(f"{qty:.6f}")

    tp1 = tp2 = None
    if decision == "BUY" and stop:
        R = entry - stop
        tp1 = entry + RR_TP1 * R
        tp2 = entry + RR_TP2 * R
    elif decision == "SELL" and stop:
        R = stop - entry
        tp1 = entry - RR_TP1 * R
        tp2 = entry - RR_TP2 * R

    return {
        "evaluated_candle_time": row["time"].to_pydatetime().isoformat(),
        "symbol": SYMBOL,
        "timeframe": TIMEFRAME,
        "decision": decision,
        "entry": round(entry, 2),
        "stop": round(stop, 2) if stop else None,
        "tp1": round(tp1, 2) if tp1 else None,
        "tp2": round(tp2, 2) if tp2 else None,
        "qty": qty,
        "balance_usdt": round(balance, 2),
        "rsi14": round(float(row["rsi14"]), 2) if not np.isnan(row["rsi14"]) else None,
        "macd": round(float(row["macd"]), 4) if not np.isnan(row["macd"]) else None,
        "macd_signal": round(float(row["macd_signal"]), 4) if not np.isnan(row["macd_signal"]) else None,
        "ema20": round(float(row["ema20"]), 2) if not np.isnan(row["ema20"]) else None,
        "ema50": round(float(row["ema50"]), 2) if not np.isnan(row["ema50"]) else None,
        "ema200": round(float(row["ema200"]), 2) if not np.isnan(row["ema200"]) else None,
        "atr14": round(float(row["atr14"]), 2) if atr_val else None,
        "patterns": patterns,
        "reason": ", ".join(reason),
        "vol_spike": bool(vol_spike),
        "breakout_up": bool(breakout_up),
        "breakdown": bool(breakdown),
    }