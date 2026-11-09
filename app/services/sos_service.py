import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.sqlalchemy_models import FallEvent, SosAlert

async def trigger_sos_for_fall(fall_event_id: int):
    """
    Background task olaraq işləyir.
    Yeni session açır (request session-u bağlanıb).
    """
    async with AsyncSessionLocal() as db:
        # FallEvent-i tap
        result = await db.execute(select(FallEvent).where(FallEvent.id == fall_event_id))
        event = result.scalar_one_or_none()
        
        if not event:
            print(f"[SOS] FallEvent {fall_event_id} tapılmadı")
            return
        
        if event.sos_triggered:
            print(f"[SOS] FallEvent {fall_event_id} artıq tetiklənib")
            return
        
        print(f"[SOS] 🚨 FALL DETECTED! Device: {event.device_id}, Prob: {event.probability:.2f}")
        
        # Stub: SosAlert yarad (channel: log)
        alert = SosAlert(
            fall_event_id=event.id,
            channel="log",
            recipient="stdout",
            status="sent",
            sent_at=event.timestamp
        )
        db.add(alert)
        
        # Event-i yenilə
        event.sos_triggered = True
        event.sos_timestamp = event.timestamp
        event.status = "confirmed"
        
        await db.commit()
        print(f"[SOS] ✅ Alert logged for event {event.id}")