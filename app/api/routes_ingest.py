from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import time

from app.api.deps import get_db
from app.services.model_service import model_service
from app.models.sqlalchemy_models import SensorReading, FallEvent, SosAlert
from app.models.pydantic_schemas import IngestPayload, IngestResponse, SensorFeatures
from app.services.sos_service import trigger_sos_for_fall  # Yaradacaq sonrakı addımda

router = APIRouter(prefix="/api/v1", tags=["Ingest"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest_sensor_data(
    payload: IngestPayload,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):

    device_id = payload.device_id
    features_list: List[float] = payload.features.to_list()
    
    
    window_array = model_service.add_sample(device_id, features_list)
    
    
    is_fall = False
    probability = 0.0
    threshold = model_service.threshold
    
    
    if window_array is not None:
        result = model_service.predict(window_array)
        is_fall = result["is_fall"]
        probability = result["probability"]
        threshold = result["threshold"]
        
        
        if is_fall:
            model_service.reset_buffer(device_id)
    
    
    ts = payload.timestamp
    if ts > 1e12:  
        from datetime import datetime, timezone
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    else:
        from datetime import datetime, timezone
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    
    reading = SensorReading(
        device_id=device_id,
        timestamp=dt,
        ax=features_list[0], ay=features_list[1], az=features_list[2],
        gx=features_list[3], gy=features_list[4], gz=features_list[5],
        fall_probability=probability,
        is_fall=is_fall,
        model_threshold=threshold
    )
    
    fall_event_id = None
    
    if is_fall:
        # 4. FallEvent yarad
        fall_event = FallEvent(
            device_id=device_id,
            timestamp=dt,
            probability=probability,
            threshold_used=threshold,
            status="detected",
            latitude=payload.latitude,
            longitude=payload.longitude,
            accuracy=payload.accuracy
        )
        db.add(fall_event)
        await db.flush()  # ID əldə etmək üçün
        
        reading.fall_event_id = fall_event.id
        fall_event_id = fall_event.id
        
        # 5. SOS Background Task (DB commit-dan sonra işləsin)
        background_tasks.add_task(trigger_sos_for_fall, fall_event_id)
    
    db.add(reading)
    await db.commit()
    
    # Cavab
    msg = "Fall detected! SOS triggered." if is_fall else "Data recorded."
    return IngestResponse(
        fall_detected=is_fall,
        probability=probability,
        threshold=threshold,
        message=msg
    )


@router.get("/falls/{device_id}", response_model=List[FallEventResponse])
async def get_fall_history(
    device_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Cihazın qəza tarixçəsini qaytarır (Admin/App UI üçün)."""
    result = await db.execute(
        select(FallEvent)
        .where(FallEvent.device_id == device_id)
        .order_by(FallEvent.timestamp.desc())
        .limit(limit)
    )
    return result.scalars().all()