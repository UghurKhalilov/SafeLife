from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Raw features (acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z)
    ax = Column(Float, nullable=False)
    ay = Column(Float, nullable=False)
    az = Column(Float, nullable=False)
    gx = Column(Float, nullable=False)
    gy = Column(Float, nullable=False)
    gz = Column(Float, nullable=False)
    
    # Model prediction result
    fall_probability = Column(Float, default=0.0)
    is_fall = Column(Boolean, default=False, index=True)
    model_threshold = Column(Float, default=0.55)
    
    # Relationship to fall event (if this reading triggered a fall)
    fall_event_id = Column(Integer, ForeignKey("fall_events.id"), nullable=True)
    fall_event = relationship("FallEvent", back_populates="trigger_reading")

    __table_args__ = (
        Index("ix_sensor_device_time", "device_id", "timestamp"),
    )


class FallEvent(Base):
    __tablename__ = "fall_events"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    probability = Column(Float, nullable=False)
    threshold_used = Column(Float, nullable=False)
    
    # Status: detected, confirmed, false_alarm, resolved
    status = Column(String(20), default="detected", index=True)
    
    # Location (optional, from phone GPS)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    
    # SOS / Response
    sos_triggered = Column(Boolean, default=False)
    sos_timestamp = Column(DateTime(timezone=True), nullable=True)
    resolved_timestamp = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationship
    trigger_reading = relationship("SensorReading", back_populates="fall_event", uselist=False)


class SosAlert(Base):
    __tablename__ = "sos_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    fall_event_id = Column(Integer, ForeignKey("fall_events.id"), nullable=False, index=True)
    fall_event = relationship("FallEvent")
    
    # Channel: telegram, fcm, sms, email, call
    channel = Column(String(20), nullable=False)
    recipient = Column(String(200), nullable=False)  # chat_id, token, phone, email
    
    status = Column(String(20), default="pending")  # pending, sent, failed, delivered
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)