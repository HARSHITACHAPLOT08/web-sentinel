import sys
print(f"Python version: {sys.version}")
try:
    import requests
    import sqlalchemy
    import apscheduler
    import bs4
    print("Core modules imported successfully.")
except Exception as e:
    print(f"Import error: {e}")

from database.db_manager import DBManager
try:
    db = DBManager()
    sites = db.get_active_websites()
    print(f"Active sites in DB: {len(sites)}")
    for s in sites:
        print(f" - {s.name}")
except Exception as e:
    print(f"DB Error: {e}")
