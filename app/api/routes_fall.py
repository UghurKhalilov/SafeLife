from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, verify_api_key
from app.models.pydantic_schemas import FallCancelRequest, FallCancelResponse
from app.services.fall_engine import fall_engine
from app.models.db_models import FallEvent, FallStatus
import uuid

router = APIRouter(prefix="/api/v1", tags=["Fall Actions"], dependencies=[Depends(verify_api_key)])

@router.post("/fall/cancel", response_model=FallCancelResponse)
def cancel_fall(payload: FallCancelRequest, db: Session = Depends(get_db)):
    success = fall_engine.user_cancelled(db, payload.event_uid)
    event = db.query(FallEvent).filter(FallEvent.event_uid == payload.event_uid).first()
    return FallCancelResponse(success=success, status=event.status if event else FallStatus.IDLE)

@router.post("/fall/trigger_sos")
def manual_sos(event_uid: uuid.UUID, db: Session = Depends(get_db)):
    event = db.query(FallEvent).filter(FallEvent.event_uid == event_uid).first()
    if not event or event.status != FallStatus.PENDING:
        raise HTTPException(400, "No active pending fall")
    
    fall_engine.manual_sos(db, event_uid)
    return {"status": "SOS_TRIGGERED_MANUALLY", "event_uid": str(event_uid)}

@router.get("/debug/active_falls")
def debug_active_falls():
    from app.services.fall_engine import fall_engine
    with fall_engine._lock:
        return {
            "pending_timers": list(fall_engine._timers.keys()),
            "location_timers": list(fall_engine._loc_timers.keys()),
            "location_counts": fall_engine._loc_counts
        }