import time
import json
import ccxt
import argparse
from config import TIMEFRAME, LOOKBACK, POLL_SECONDS
from data import init_exchange, fetch_ohlcv
from signals import build_features, generate_signal_row
from logger import append_log
from notifications import notify

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Live Signal Bot for Crypto Trading")
    parser.add_argument("--symbol", type=str, required=True, help="Trading pair, e.g., BTC/USDT")
    return parser.parse_args()

def main():
    args = parse_args()
    SYMBOL = args.symbol
    exchange = init_exchange()
    last_closed_time = None
    print(json.dumps({"status": "starting", "symbol": SYMBOL, "timeframe": TIMEFRAME}))
    
    while True:
        try:
            df = fetch_ohlcv(exchange, SYMBOL, TIMEFRAME, LOOKBACK)
            if len(df) < 50:
                time.sleep(POLL_SECONDS)
                continue

            feats = build_features(df, exchange)
            closed_time = feats["time"].iloc[-2]

            if last_closed_time is None or closed_time != last_closed_time:
                sig = generate_signal_row(feats, exchange,SYMBOL)
                last_closed_time = closed_time

                if sig is not None:
                    print(json.dumps(sig, ensure_ascii=False))
                    append_log(sig)
                    notify(sig)  # Send notifications for BUY/SELL signals
                else:
                    print(json.dumps({"info": "not_enough_data"}))

        except ccxt.NetworkError as e:
            print(json.dumps({"error": "network", "detail": str(e)}))
        except ccxt.ExchangeError as e:
            print(json.dumps({"error": "exchange", "detail": str(e)}))
        except Exception as e:
            print(json.dumps({"error": "unknown", "detail": str(e)}))

        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()