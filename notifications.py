# from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
from telegram import Bot
import asyncio
# from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, WHATSAPP_TO
# from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER, SMTP_SERVER, SMTP_PORT
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def format_signal_message(signal: dict) -> str:
    """Format signal data into a concise message."""
    return (
        f"🚨 New {signal['decision']} Signal for {signal['symbol']} ({signal['timeframe']})\n"
        f"Time: {signal['evaluated_candle_time']}\n"
        f"Entry: ${signal['entry']}\n"
        f"Stop Loss: ${signal['stop']}\n"
        f"Take Profit 1: ${signal['tp1']}\n"
        f"Take Profit 2: ${signal['tp2']}\n"
        f"Quantity: {signal['qty']}\n"
        f"Reason: {signal['reason']}\n"
        f"Patterns: {', '.join(signal['patterns']) if signal['patterns'] else 'None'}\n"
        f"RSI: {signal['rsi14']}\n"
        f"MACD: {signal['macd']}\n"
        f"Balance: ${signal['balance_usdt']}"
    )

async def send_telegram_message(signal: dict) -> bool:
    """Send signal to Telegram using python-telegram-bot."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[WARN] Telegram credentials not set. Skipping Telegram notification.")
        return False
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=format_signal_message(signal)
        )
        print("[INFO] Telegram message sent successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")
        return False

def notify(signal: dict) -> None:
    """Send notifications for BUY or SELL signals."""
    if signal["decision"] not in ("BUY", "SELL"):
        return
    # send_whatsapp_message(signal)
    # send_email_message(signal)
    # Run async Telegram send in a synchronous context
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_telegram_message(signal))

# def send_whatsapp_message(signal: dict) -> bool:
#     """Send signal to WhatsApp using Twilio."""
#     if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
#         print("[WARN] Twilio credentials not set. Skipping WhatsApp notification.")
#         return False
#     try:
#         client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
#         message = client.messages.create(
#             body=format_signal_message(signal),
#             from_=TWILIO_WHATSAPP_FROM,
#             to=WHATSAPP_TO
#         )
#         print(f"[INFO] WhatsApp message sent: SID {message.sid}")
#         return True
#     except Exception as e:
#         print(f"[ERROR] Failed to send WhatsApp message: {e}")
#         return False

# def send_email_message(signal: dict) -> bool:
#     """Send signal to email using smtplib."""
#     if not EMAIL_PASSWORD:
#         print("[WARN] Email password not set. Skipping email notification.")
#         return False
#     try:
#         msg = MIMEText(format_signal_message(signal))
#         msg["Subject"] = f"{signal['decision']} Signal for {signal['symbol']}"
#         msg["From"] = EMAIL_SENDER
#         msg["To"] = EMAIL_RECEIVER

#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.starttls()
#             server.login(EMAIL_SENDER, EMAIL_PASSWORD)
#             server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
#         print("[INFO] Email sent successfully")
#         return True
#     except Exception as e:
#         print(f"[ERROR] Failed to send email: {e}")
#         return False

