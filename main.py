from apscheduler.schedulers.background import BackgroundScheduler
from database.db_manager import DBManager
from monitors.checker import SiteChecker
import time
import signal
import sys

def check_task(site_id, checker):
    try:
        checker.check_site(site_id)
    except Exception as e:
        print(f"Error checking site {site_id}: {e}")

def main():
    print("Initializing Website Monitoring System...")
    db = DBManager()
    checker = SiteChecker(db)
    scheduler = BackgroundScheduler()
    
    # Load active websites and schedule them
    websites = db.get_active_websites()
    for site in websites:
        print(f"[*] Scheduling {site.name} every {site.check_interval}s")
        scheduler.add_job(
            check_task, 
            'interval', 
            seconds=site.check_interval, 
            args=[site.id, checker],
            id=f"site_{site.id}"
        )
    
    scheduler.start()
    print("Scheduler started. Monitoring active websites.")

    # Graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutting down scheduler...")
        scheduler.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
            # Future Improvement: Periodically check DB for new sites to add to scheduler
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == "__main__":
    main()
