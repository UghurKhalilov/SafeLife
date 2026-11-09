from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

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
