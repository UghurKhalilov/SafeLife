from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_api_key
from app.models.pydantic_schemas import IngestBatchRequest, IngestResponse
from app.models.db_models import User, SensorData, FallEvent, FallStatus
from app.services.model_service import model_service
from app.services.fall_engine import fall_engine
import json
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1", tags=["Ingestion"], dependencies=[Depends(verify_api_key)])

@router.post("/ingest", response_model=IngestResponse)
def ingest_batch(payload: IngestBatchRequest, db: Session = Depends(get_db)):
    if not payload.readings:
        return IngestResponse(received=0)

    # 1. User Get/Create
    user = db.query(User).filter(User.id == payload.device_id).first()
    if not user:
        user = User(id=payload.device_id, username=f"User_{payload.device_id[:8]}")
        db.add(user)
        db.flush()

    # 2. Bulk Insert Sensor Data
    sensor_objs = [
        SensorData(
            user_id=payload.device_id, timestamp=r.timestamp,
            acc_x=r.acc_x, acc_y=r.acc_y, acc_z=r.acc_z,
            gyro_x=r.gyro_x, gyro_y=r.gyro_y, gyro_z=r.gyro_z,
            gps_lat=r.gps_lat, gps_lon=r.gps_lon
        ) for r in payload.readings
    ]
    db.bulk_save_objects(sensor_objs)
    db.commit()

    # 3. AI Inference
    detections = model_service.process_batch(payload.device_id, payload.readings)
    
    fall_detected = next((d for d in detections if d['is_fall']), None)
    
    if fall_detected:
        # 4. Create Fall Event
        event = FallEvent(
            user_id=payload.device_id,
            status=FallStatus.PENDING,
            probability=fall_detected['probability'],
            gps_lat=fall_detected.get('gps_lat'),
            gps_lon=fall_detected.get('gps_lon'),
            medical_info=user.medical_info,
            meta_data=json.dumps({"detection": fall_detected})
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        # 5. Trigger Fall Engine (Background Thread)
        fall_engine.trigger_fall(db, event)

        return IngestResponse(
            received=len(sensor_objs),
            action="START_ALARM_15S",
            event_uid=event.event_uid,
            probability=fall_detected['probability'],
            message=f"Fall detected ({fall_detected['probability']*100:.0f}%). Start 15s countdown."
        )

    return IngestResponse(received=len(sensor_objs), action="NONE")