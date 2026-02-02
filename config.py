import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./monitor.db")
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Monitoring Defaults
    DEFAULT_INTERVAL = 60  # seconds
    REQUEST_TIMEOUT = 10   # seconds
    
    # OSINT / Content Change
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WebsiteMonitor/1.0"
    
    # Alerting Thresholds
    CONSECUTIVE_FAILURES_THRESHOLD = int(os.getenv("FAILURE_THRESHOLD", 3))
    RESPONSE_TIME_THRESHOLD = float(os.getenv("MAX_RESPONSE_TIME", 5.0)) # seconds
