from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class SensorFeatures(BaseModel):
    """6 feature: ax, ay, az, gx, gy, gz"""
    ax: float = Field(..., description="Accelerometer X (m/s²)")
    ay: float = Field(..., description="Accelerometer Y (m/s²)")
    az: float = Field(..., description="Accelerometer Z (m/s²)")
    gx: float = Field(..., description="Gyroscope X (rad/s)")
    gy: float = Field(..., description="Gyroscope Y (rad/s)")
    gz: float = Field(..., description="Gyroscope Z (rad/s)")

    def to_list(self) -> List[float]:
        """Model Service Buffer üçün sıralı listə çevirir."""
        return [self.ax, self.ay, self.az, self.gx, self.gy, self.gz]


class IngestPayload(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=100, description="Unique device/user ID")
    timestamp: int = Field(..., description="Unix timestamp (milliseconds or seconds)")
    features: SensorFeatures
    
    # Optional location (Android GPS varsa)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None


# --- API Cavabı ---
class IngestResponse(BaseModel):
    status: str = "ok"
    fall_detected: bool
    probability: float
    threshold: float
    message: Optional[str] = None


# --- Health Check (Artıq var, yenidən yoxlamaq üçün) ---
class HealthResponse(BaseModel):
    status: str
    database: str
    ai_model_loaded: bool
    threshold: float


# --- Fall Event (Frontend/Admin Panel üçün) ---
class FallEventResponse(BaseModel):
    id: int
    device_id: str
    timestamp: datetime
    probability: float
    status: str
    latitude: Optional[float]
    longitude: Optional[float]
    sos_triggered: bool

    class Config:
        from_attributes = True


# --- Data Collection (Training Data) ---
class CollectLabel(str, Enum):
    WALK = "walk"
    RUN = "run"
    PHONE_DROP = "phone_drop"
    FALL = "fall"
    CRASH_SIM = "crash_sim"


class CollectSample(BaseModel):
    """Single sensor sample for training data collection."""
    timestamp: int = Field(..., description="Unix timestamp (milliseconds)")
    ax: float = Field(..., description="Accelerometer X (m/s²)")
    ay: float = Field(..., description="Accelerometer Y (m/s²)")
    az: float = Field(..., description="Accelerometer Z (m/s²)")
    gx: float = Field(..., description="Gyroscope X (rad/s)")
    gy: float = Field(..., description="Gyroscope Y (rad/s)")
    gz: float = Field(..., description="Gyroscope Z (rad/s)")
    speed: float = Field(..., description="Speed (m/s)")
    latitude: float = Field(..., description="Latitude (degrees)")
    longitude: float = Field(..., description="Longitude (degrees)")


class CollectPayload(BaseModel):
    device_id: str = Field(
        ...,
        pattern=r"^[A-Za-z0-9_-]{1,64}$",
        description="Device ID (alphanumeric, underscore, hyphen, max 64 chars)"
    )
    session_id: str = Field(
        ...,
        pattern=r"^[A-Za-z0-9_-]{1,64}$",
        description="Session ID (alphanumeric, underscore, hyphen, max 64 chars)"
    )
    label: CollectLabel = Field(..., description="Activity label")
    samples: List[CollectSample] = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="List of sensor samples (max 5000)"
    )


class CollectResponse(BaseModel):
    status: str = "ok"
    file_path: str
    sample_count: int
    message: Optional[str] = None
