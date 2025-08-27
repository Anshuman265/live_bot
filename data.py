import ccxt
import pandas as pd
from config import EXCHANGE_ID, API_KEY, API_SECRET,TIMEFRAME, LOOKBACK, QUOTE_CCY

def init_exchange():
    exchange = getattr(ccxt, EXCHANGE_ID)({
        "apiKey": API_KEY,
        "secret": API_SECRET,
        "enableRateLimit": True,
    })
    # Configure for spot market; modify for futures if needed
    # exchange.options["defaultType"] = "future"
    return exchange

def fetch_ohlcv(exchange, symbol, timeframe: str = TIMEFRAME, limit: int = LOOKBACK) -> pd.DataFrame:
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=["time", "open", "high", "low", "close", "volume"])
    df["time"] = pd.to_datetime(df["time"], unit="ms", utc=True)
    return df

def fetch_balance_usdt(exchange, quote: str = QUOTE_CCY) -> float:
    try:
        bal = exchange.fetch_balance()
        val = bal.get(quote, {}).get("free", None)
        if val is None:
            val = bal.get(quote, {}).get("total", 0.0)
        return float(val or 0.0)
    except Exception:
        return 0.0