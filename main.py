import os
import re
import asyncio
import logging
from datetime import date
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import nest_asyncio

# === LOGGING SETUP ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")
KEYWORDS = ['RELAX', 'LUX', "MO'TABAR", 'MO‘TABAR', 'NIXOL']

if not BOT_TOKEN or not TARGET_CHANNEL:
    raise EnvironmentError("BOT_TOKEN or TARGET_CHANNEL not set in environment variables.")

# === CLEANING HELPERS ===
def remove_emojis(text):
    return re.sub(r'[\U00010000-\U0010ffff\U0001F300-\U0001F6FF\U0001F1E0-\U0001F1FF]+', '', text)

def is_valid_row(line):
    clean_line = remove_emojis(line).strip()
    return any(k in clean_line.upper() for k in KEYWORDS) and '/50' in clean_line

def clean_row(line):
    return re.sub(' +', ' ', remove_emojis(line)).strip()

# === HANDLER ===
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.text:
        message = update.channel_post.text
        logger.info(f"\n📡 Channel post received:\n{message}\n---")

        rows = message.split('\n')
        for row in rows:
            logger.debug(f"🔍 Checking row: {row}")
            if is_valid_row(row):
                cleaned = clean_row(row)
                today = date.today().isoformat()
                message_to_send = f"{today} | {cleaned}"
                logger.info(f"✅ Sending: {message_to_send}")
                await context.bot.send_message(chat_id=TARGET_CHANNEL, text=message_to_send)
                await asyncio.sleep(5)
            else:
                logger.debug("⏭️ Skipped row.")

# === MAIN ===
async def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POST & filters.TEXT, handle_channel_post))
    logger.info("🚀 Bot is running and watching @datatodashboards (channel posts)...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    while True:
        await asyncio.sleep(3600)

# === EXECUTION ===
nest_asyncio.apply()
loop = asyncio.get_event_loop()
loop.create_task(run_bot())
loop.run_forever()
