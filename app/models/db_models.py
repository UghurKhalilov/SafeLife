from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

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