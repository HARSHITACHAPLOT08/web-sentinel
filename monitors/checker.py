import requests
import time
from datetime import datetime
from database.db_manager import DBManager
from .content_diff import get_content_hash, detect_change
from alerts.telegram_bot import TelegramBot
from config import Config

class SiteChecker:
    def __init__(self, db_manager: DBManager):
        self.db = db_manager
        self.notifier = TelegramBot()

    def check_site(self, website_id: int):
        with self.db.get_session() as session:
            # Need to re-query within the session for thread safety
            from database.models import Website
            website = session.query(Website).get(website_id)
            if not website:
                return

            print(f"[*] Checking {website.name} ({website.url})...")
            start_time = time.time()
            
            try:
                response = requests.get(
                    website.url, 
                    timeout=Config.REQUEST_TIMEOUT,
                    headers={"User-Agent": Config.USER_AGENT}
                )
                response_time = time.time() - start_time
                status_code = response.status_code
                is_up = status_code < 400
                content_hash = get_content_hash(response.text)
                error_msg = None
            except Exception as e:
                response_time = time.time() - start_time
                status_code = 0
                is_up = False
                content_hash = None
                error_msg = str(e)

            # --- Evaluate Status Changes ---
            was_up = website.is_up
            old_hash = website.last_content_hash
            
            # --- Logic: Handle Alerts ---
            
            # 1. UP/DOWN Alerts
            if is_up:
                website.consecutive_failures = 0
                if not was_up:
                    website.is_up = True
                    self._trigger_alert(website, "UP", f"RECOVERED: {website.name} is back online!")
            else:
                website.consecutive_failures += 1
                if was_up and website.consecutive_failures >= Config.CONSECUTIVE_FAILURES_THRESHOLD:
                    website.is_up = False
                    self._trigger_alert(website, "DOWN", f"DOWN: {website.name} is unreachable!\nReason: {error_msg or f'Status {status_code}'}")

            # 2. Content Change (OSINT)
            if is_up and website.last_content_hash and detect_change(website.last_content_hash, content_hash):
                self._trigger_alert(website, "CONTENT_CHANGE", f"CHANGE DETECTED: Content modified on {website.name}!")

            # 3. Slow Response
            if is_up and response_time > Config.RESPONSE_TIME_THRESHOLD:
                self._trigger_alert(website, "SLOW_RESPONSE", f"SLOW: {website.name} response time: {response_time:.2f}s")

            # --- Update Website State ---
            website.last_status_code = status_code
            website.last_response_time = response_time
            website.last_check_at = datetime.utcnow()
            website.last_content_hash = content_hash or website.last_content_hash
            
            # --- Log result ---
            from database.models import CheckLog
            log = CheckLog(
                website_id=website.id,
                status_code=status_code,
                response_time=response_time,
                is_up=is_up,
                content_hash=content_hash,
                error_message=error_msg
            )
            session.add(log)
            # Commit happens via DBManager's context manager

    def _trigger_alert(self, website, alert_type, message):
        print(f"[!] Alert: {message}")
        # Add to DB
        from database.models import AlertLog
        alert = AlertLog(website_id=website.id, alert_type=alert_type, message=message)
        # We handle session via the caller's session, but for AlertLog we might want a separate entry
        # Actually, since we are inside a context manager, adding to session is fine.
        # But we need to ensure the session is passed or accessible.
        # In this implementation, check_site holds the session.
        # So we should pass the session or just rely on the fact that 'website' is attached to it.
        website.alerts.append(alert)
        
        # Send Notification
        self.notifier.send_message(message, website_id=website.id, alert_type=alert_type)
