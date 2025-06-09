import os
import re
import asyncio
import requests
from datetime import date
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters
import nest_asyncio

# === CONFIG ===
BOT_TOKEN = '7859097671:AAFFSVN6qM2Mb_fjcq23CvLso4HFSnFaRCE'
TARGET_CHANNEL = '@datafilterforodoo'
ZAP_WEBHOOK_URL = 'https://hooks.zapier.com/hooks/catch/20489032/2vzvvrp/'
KEYWORDS = ['RELAX', 'LUX', "MO'TABAR", 'MO‘TABAR', 'NIXOL']

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
        print(f"\n📡 Channel post received:\n{message}\n---")

        rows = message.split('\n')
        for row in rows:
            print(f"🔍 Checking row: {row}")
            if is_valid_row(row):
                cleaned = clean_row(row)
                today = date.today().isoformat()
                message_to_send = f"{today} | {cleaned}"
                print(f"✅ Message to send: {message_to_send}")

                # Send to Telegram
                await context.bot.send_message(chat_id=TARGET_CHANNEL, text=message_to_send)

                # Send to Zapier
                try:
                    response = requests.post(
                        ZAP_WEBHOOK_URL,
                        json={"message": message_to_send}
                    )
                    print(f"🌐 Sent to Zapier: {response.status_code}")
                except Exception as e:
                    print(f"❌ Zapier error: {e}")

                await asyncio.sleep(5)
            else:
                print("⏭️ Skipped row.")

# === MAIN ===
async def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL & filters.TEXT, handle_channel_post))
    print("🚀 Bot is running and watching @datatodashboards (channel posts)...")
    await app.run_polling()

# === EXECUTION ===
nest_asyncio.apply()
asyncio.run(run_bot())
