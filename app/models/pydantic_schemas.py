from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Literal
import uuid
from app.models.db_models import FallStatus

# --- Sensor Ingestion ---
class SensorReading(BaseModel):
    timestamp: datetime
    acc_x: float; acc_y: float; acc_z: float
    gyro_x: float; gyro_y: float; gyro_z: float
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None

class IngestBatchRequest(BaseModel):
    device_id: str
    readings: List[SensorReading]

class IngestResponse(BaseModel):
    received: int
    action: Literal["NONE", "START_ALARM_15S"] = "NONE"
    event_uid: Optional[uuid.UUID] = None
    probability: Optional[float] = None
    message: str = "OK"

# --- Fall Actions ---
class FallCancelRequest(BaseModel):
    event_uid: uuid.UUID

class FallCancelResponse(BaseModel):
    success: bool
    status: FallStatus

# --- Health / Debug ---
class HealthResponse(BaseModel):
    status: str
    database: str
    ai_model_loaded: bool  
    threshold: float
