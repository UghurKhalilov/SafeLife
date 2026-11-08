import uuid
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.database import Base
from datetime import datetime, timezone

class FallStatus(str, enum.Enum):
    IDLE = "IDLE"
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    RESOLVED = "RESOLVED"

class User(Base):
    __tablename__ = "users"
    id = Column(String(64), primary_key=True)  # device_id
    username = Column(String(100))
    medical_info = Column(Text, nullable=True)
    
    contacts = relationship("TrustedContact", back_populates="user", cascade="all, delete-orphan")
    fall_events = relationship("FallEvent", back_populates="user", cascade="all, delete-orphan")
    sensor_data = relationship("SensorData", back_populates="user", cascade="all, delete-orphan")

class TrustedContact(Base):
    __tablename__ = "trusted_contacts"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(64), ForeignKey("users.id"), index=True)
    name = Column(String(100))
    phone = Column(String(20))
    priority = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    user = relationship("User", back_populates="contacts")

class SensorData(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), index=True)
    timestamp = Column(DateTime(timezone=True), index=True)
    
    acc_x = Column(Float); acc_y = Column(Float); acc_z = Column(Float)
    gyro_x = Column(Float); gyro_y = Column(Float); gyro_z = Column(Float)
    gps_lat = Column(Float, nullable=True); gps_lon = Column(Float, nullable=True)
    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="sensor_data")

class FallEvent(Base):
    __tablename__ = "fall_events"
    id = Column(Integer, primary_key=True, index=True)
    event_uid = Column(PG_UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    user_id = Column(String(64), ForeignKey("users.id"), index=True)
    
    status = Column(SQLEnum(FallStatus), default=FallStatus.IDLE, index=True)
    probability = Column(Float)
    gps_lat = Column(Float, nullable=True); gps_lon = Column(Float, nullable=True)
    medical_info = Column(Text, nullable=True)
    triggered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    meta_data = Column(Text, nullable=True)  
    
    user = relationship("User", back_populates="fall_events")