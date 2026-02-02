import requests
from config import Config
import time

class TelegramBot:
    def __init__(self, token=Config.TELEGRAM_BOT_TOKEN, chat_id=Config.TELEGRAM_CHAT_ID):
        self.token = token
        self.chat_id = chat_id
        self.last_sent = {} # Rate limiting: {website_id_alert_type: timestamp}
        self.cooldown = 600 # 10 minutes cooldown for same alert type per site

    def send_message(self, message: str, website_id: int = None, alert_type: str = None):
        if not self.token or not self.chat_id:
            print(f"[LOCAL ALERT] {message}")
            return False

        # Basic Rate Limiting
        if website_id and alert_type:
            key = f"{website_id}_{alert_type}"
            now = time.time()
            if key in self.last_sent and (now - self.last_sent[key]) < self.cooldown:
                print(f"Alert suppressed (rate limit): {key}")
                return False
            self.last_sent[key] = now

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return False
