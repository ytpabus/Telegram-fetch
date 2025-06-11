from telethon import TelegramClient, events
import asyncio
import re
import requests
from datetime import date

# === CONFIG ===
api_id = 26347537
api_hash = '68a4fac4e5b6c85067787bbc2f343631'
source_channel = 'https://t.me/datatodashboards'
zap_webhook_url = 'https://hooks.zapier.com/hooks/catch/20489032/2vzvvrp/'
keywords = ['RELAX', 'LUX', "MO'TABAR", 'MO‘TABAR', 'NIXOL']

client = TelegramClient('session_name', api_id, api_hash)

def remove_emojis(text):
    return re.sub(r'[\U00010000-\U0010ffff\U0001F300-\U0001F6FF\U0001F1E0-\U0001F1FF]+', '', text)

def emoji_before_50_to_v(text):
    # Replace emojis right before /50 (no matter how many) with " V/50"
    text = re.sub(
        r'(\S)[\U00010000-\U0010ffff\U0001F300-\U0001F6FF\U0001F1E0-\U0001F1FF]+/50',
        r'\1 V/50',
        text
    )
    # Remove all other emojis
    text = remove_emojis(text)
    # Clean up spaces
    text = re.sub(' +', ' ', text)
    # Force any v/50 to uppercase
    text = re.sub(r'\bv/50\b', 'V/50', text, flags=re.IGNORECASE)
    return text.strip()

def is_valid_row(line):
    clean_line = line.strip()  # Emojis already removed
    return any(k in clean_line.upper() for k in keywords) and '/50' in clean_line

@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    try:
        msg_text = event.message.text or event.message.caption
        if not msg_text:
            return

        print(f"\n📡 New message received:\n{msg_text}\n---")
        rows = msg_text.split('\n')
        for row in rows:
            # STEP 1: Transform row (emojis before /50 to V/50, all other emojis removed)
            processed_row = emoji_before_50_to_v(row)
            # STEP 2: Validate after processing
            if is_valid_row(processed_row):
                today = date.today().isoformat()
                message_to_send = f"{today} | {processed_row}"
                print(f"✅ Sending: {message_to_send}")

                try:
                    response = requests.post(
                        zap_webhook_url,
                        json={"message": message_to_send}
                    )
                    print(f"🌐 Sent to Zapier: {response.status_code}")
                except Exception as e:
                    print(f"❌ Zapier error: {e}")

                await asyncio.sleep(5)
            else:
                print("⏭️ Skipped row.")
    except Exception as e:
        print(f"Error: {e}")

async def main():
    print("🚀 Bot is running, watching for new messages...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
