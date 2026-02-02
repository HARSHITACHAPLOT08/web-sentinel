from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Website(Base):
    __tablename__ = 'websites'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False, unique=True)
    check_interval = Column(Integer, default=60) # in seconds
    is_active = Column(Boolean, default=True)
    
    # Monitoring State
    is_up = Column(Boolean, default=True)
    last_status_code = Column(Integer)
    last_response_time = Column(Float)
    last_check_at = Column(DateTime)
    last_content_hash = Column(String(64))
    consecutive_failures = Column(Integer, default=0)
    
    logs = relationship("CheckLog", back_populates="website", cascade="all, delete-orphan")
    alerts = relationship("AlertLog", back_populates="website", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Website(name='{self.name}', url='{self.url}', is_up={self.is_up})>"

class CheckLog(Base):
    __tablename__ = 'check_logs'
    
    id = Column(Integer, primary_key=True)
    website_id = Column(Integer, ForeignKey('websites.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    status_code = Column(Integer)
    response_time = Column(Float)
    is_up = Column(Boolean)
    content_hash = Column(String(64))
    error_message = Column(Text)
    
    website = relationship("Website", back_populates="logs")

class AlertLog(Base):
    __tablename__ = 'alert_logs'
    
    id = Column(Integer, primary_key=True)
    website_id = Column(Integer, ForeignKey('websites.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    alert_type = Column(String(50)) # DOWN, UP, CONTENT_CHANGE, SLOW_RESPONSE
    message = Column(Text)
    
    website = relationship("Website", back_populates="alerts")
