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

def process_row(row):
    # Step 1: Replace emojis after keyword (and before /50) with a space
    row = re.sub(
        r'(' + '|'.join(re.escape(k) for k in keywords) + r')'
        r'[\U00010000-\U0010ffff\U0001F300-\U0001F6FF\U0001F1E0-\U0001F1FF]+(?=/50)',
        r'\1 ', row, flags=re.IGNORECASE
    )
    # Step 2: If only whitespace before /50, make it V/50 (insert space if needed)
    row = re.sub(r'(\s*)/50', r'\1V/50', row)
    # Step 3: Remove any remaining emojis
    row = remove_emojis(row)
    # Step 4: Cleanup multiple spaces
    row = re.sub(' +', ' ', row)
    # Step 5: Uppercase V/50
    row = re.sub(r'\bv/50\b', 'V/50', row, flags=re.IGNORECASE)
    return row.strip()

def is_valid_row(row):
    clean_row = row.strip().upper()
    return any(k in clean_row for k in keywords) and '/50' in clean_row

@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    try:
        msg_text = event.message.text or event.message.caption
        if not msg_text:
            return

        print(f"\n📡 New message received:\n{msg_text}\n---")
        rows = msg_text.split('\n')
        for row in rows:
            processed_row = process_row(row)
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
