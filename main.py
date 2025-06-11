from telethon import TelegramClient, events
import asyncio
import re
import requests
from datetime import date
import nest_asyncio

# === CONFIG ===
api_id = 26347537  # Replace with your API ID
api_hash = '68a4fac4e5b6c85067787bbc2f343631'  # Replace with your API HASH
source_channel = 'https://t.me/datatodashboards'  # Channel 1 (Listening)
zap_webhook_url = 'https://hooks.zapier.com/hooks/catch/20489032/2vzvvrp/'
keywords = ['RELAX', 'LUX', "MO'TABAR", 'MO‘TABAR', 'NIXOL']

# === CLIENT SESSION ===
client = TelegramClient('session_name', api_id, api_hash)

# === CLEANING HELPERS ===
def remove_emojis(text):
    return re.sub(r'[\U00010000-\U0010ffff\U0001F300-\U0001F6FF\U0001F1E0-\U0001F1FF]+', '', text)

def is_valid_row(line):
    clean_line = remove_emojis(line).strip()
    return any(k in clean_line.upper() for k in keywords) and '/50' in clean_line

def clean_row(line):
    return re.sub(' +', ' ', remove_emojis(line)).strip()

# === TELEGRAM EVENT HANDLER ===
@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    try:
        msg_text = event.message.text or event.message.caption
        if not msg_text:
            return  # Ignore messages without text or captions

        print(f"\n📡 New message received:\n{msg_text}\n---")

        rows = msg_text.split('\n')
        for row in rows:
            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            # Replace emojis immediately before /50 with 'v/50'
            row = re.sub(
                r'([\w ]+)[\U00010000-\U0010ffff\U0001F300-\U0001F6FF\U0001F1E0-\U0001F1FF]+/50',
                r'\1 v/50',
                row
            )
            # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            print(f"🔍 Checking row: {row}")
            if is_valid_row(row):
                cleaned = clean_row(row)
                today = date.today().isoformat()
                message_to_send = f"{today} | {cleaned}"
                print(f"✅ Sending: {message_to_send}")

                # Send to Zapier
                try:
                    response = requests.post(
                        zap_webhook_url,
                        json={"message": message_to_send}
                    )
                    print(f"🌐 Sent to Zapier: {response.status_code}")
                except Exception as e:
                    print(f"❌ Zapier error: {e}")

                await asyncio.sleep(5)  # Interval between messages
            else:
                print("⏭️ Skipped row.")
    except Exception as e:
        print(f"Error: {e}")

# === MAIN FUNCTION ===
async def main():
    print("🚀 Bot is running, watching for new messages...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
