import os
import json
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import InputMessagesFilterPhotos
from dotenv import load_dotenv
import asyncio

# Setup logging
os.makedirs('data/logs', exist_ok=True)
logging.basicConfig(
    filename='data/logs/scrape.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()
api_id = int(os.getenv('TELEGRAM_API_ID'))  # Convert to int
api_hash = os.getenv('TELEGRAM_API_HASH')
phone = os.getenv('TELEGRAM_PHONE')
channels = os.getenv('TELEGRAM_CHANNELS').split(',')

async def scrape_telegram_data():
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start(phone=phone)
    try:
        for channel in channels:
            channel = channel.strip()
            logging.info(f"Scraping channel: {channel}")
            date_str = datetime.now().strftime("%Y-%m-%d")
            os.makedirs(f'data/raw/telegram_messages/{date_str}/{channel}', exist_ok=True)
            
            messages_data = []
            async for message in client.iter_messages(f'@{channel}', limit=100, filter=InputMessagesFilterPhotos):
                message_info = {
                    'message_id': message.id,
                    'date': message.date.isoformat(),
                    'text': message.text or '',
                    'sender_id': message.sender_id,
                    'has_photo': bool(message.photo),
                    'channel': channel
                }
                if message.photo:
                    photo_path = f'photos/{channel}_{message.id}.jpg'
                    os.makedirs('photos', exist_ok=True)
                    await message.download_media(file=photo_path)
                    message_info['photo_path'] = photo_path
                else:
                    message_info['photo_path'] = None
                messages_data.append(message_info)
            
            # Save to JSON
            output_path = f'data/raw/telegram_messages/{date_str}/{channel}/messages.json'
            with open(output_path, 'w') as f:
                json.dump(messages_data, f, indent=2)
            logging.info(f"Saved {len(messages_data)} messages to {output_path}")
    except Exception as e:
        logging.error(f"Error scraping Telegram data: {e}")
        raise
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(scrape_telegram_data())
