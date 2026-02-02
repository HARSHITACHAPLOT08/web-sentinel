from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from .models import Base, Website, CheckLog, AlertLog
from config import Config
from contextlib import contextmanager

class DBManager:
    def __init__(self, db_url=Config.DATABASE_URL):
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False} if "sqlite" in db_url else {})
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    @contextmanager
    def get_session(self) -> Session:
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            # If it's an integrity error, we might want to handle it specifically
            # but for now we just re-raise and let the caller decide
            raise e
        finally:
            session.close()

    def add_website(self, name: str, url: str, interval: int = 60):
        session = self.SessionLocal()
        try:
            # Check if URL already exists
            existing = session.query(Website).filter(Website.url == url).first()
            if existing:
                session.close()
                return None
                
            website = Website(name=name, url=url, check_interval=interval)
            session.add(website)
            session.commit()
            session.refresh(website)
            session.expunge(website)
            return website
        except Exception:
            session.rollback()
            return None
        finally:
            session.close()

    def get_all_websites(self):
        with self.get_session() as session:
            sites = session.query(Website).all()
            session.expunge_all()
            return sites

    def get_active_websites(self):
        with self.get_session() as session:
            sites = session.query(Website).filter(Website.is_active == True).all()
            session.expunge_all()
            return sites

    def update_website_status(self, website_id: int, **kwargs):
        with self.get_session() as session:
            session.query(Website).filter(Website.id == website_id).update(kwargs)

    def add_check_log(self, website_id: int, **kwargs):
        with self.get_session() as session:
            log = CheckLog(website_id=website_id, **kwargs)
            session.add(log)
            return log

    def add_alert_log(self, website_id: int, alert_type: str, message: str):
        with self.get_session() as session:
            alert = AlertLog(website_id=website_id, alert_type=alert_type, message=message)
            session.add(alert)
            return alert
