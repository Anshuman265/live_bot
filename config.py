import os
from dotenv import load_dotenv

# Load environment variables from .env file
#load_dotenv()

# Exchange configuration
EXCHANGE_ID = "binance"   # e.g., 'binance', 'bybit', 'kucoin'
API_KEY = os.getenv("API_KEY")             # Set if fetching balances or trading
API_SECRET = os.getenv("API_SECRET")
QUOTE_CCY = "USDT"        # For balance fetching

# Trading parameters
#SYMBOL = "BTC/USDT"
TIMEFRAME = "1m"          # e.g., '1m', '5m', '15m', '1h', '4h', '1d'
LOOKBACK = 300            # Candles to fetch
POLL_SECONDS = 30         # Polling interval for new candles
RISK_PER_TRADE = 0.01     # 1% of account
RR_TP1 = 1.5              # Take-profit 1 at 1.5R
RR_TP2 = 2.5              # Take-profit 2 at 2.5R
USE_ATR_SL = True         # Use ATR-based stop-loss (False for swing-based)
ATR_MULT = 1.5            # ATR multiple for SL/TP
S_R_WINDOW = 20           # Bars for swing high/low
VOL_SPIKE_MULT = 1.1      # Volume spike threshold vs SMA20
LOG_PATH = "signals_log.csv"

# Notification Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") # Telegram bot token
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")      # Your chat ID, e.g., "-123456789" or "123456789"