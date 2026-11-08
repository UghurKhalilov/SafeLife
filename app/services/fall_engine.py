import asyncio
import threading
import uuid
import json
from datetime import datetime, timezone
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.sos_service import sos_service
from app.services.model_service import model_service
from app.config import settings
from app.models.db_models import FallEvent, FallStatus, User
from app.database import AsyncSessionLocal

class FallEngine:
    def __init__(self):
        self._timers: Dict[str, threading.Timer] = {}
        self._loc_timers: Dict[str, threading.Timer] = {}
        self._loc_counts: Dict[str, int] = {}
        self._lock = threading.Lock()

    def _get_new_session(self) -> AsyncSession:
        return AsyncSessionLocal()

    def _run_async(self, coro):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    def trigger_fall(self, db, event: FallEvent):
        print(f"[FallEngine] FALL DETECTED: {event.event_uid} | Prob: {event.probability:.2f}")
        event.status = FallStatus.PENDING
        timer = threading.Timer(settings.SOS_TIMEOUT_SECONDS, self._on_timeout, args=[event.event_uid])
        timer.daemon = True
        timer.start()
        with self._lock:
            self._timers[str(event.event_uid)] = timer
        print(f"[FallEngine] 15s Countdown STARTED for {event.event_uid}")

    def user_cancelled(self, event_uid: uuid.UUID) -> bool:
        with self._lock:
            timer = self._timers.pop(str(event_uid), None)
        if timer:
            timer.cancel()
            print(f"[FallEngine] CANCELLED by User: {event_uid}")
            self._run_async(self._do_cancel(event_uid))
            return True
        return False

    def manual_sos(self, event_uid: uuid.UUID):
        with self._lock:
            timer = self._timers.pop(str(event_uid), None)
        if timer: timer.cancel()
        self._run_async(self._do_manual_sos(event_uid))

    async def _do_cancel(self, event_uid: uuid.UUID):
        async with self._get_new_session() as db:
            res = await db.execute(select(FallEvent).where(FallEvent.event_uid == event_uid))
            event = res.scalar_one_or_none()
            if event and event.status == FallStatus.PENDING:
                event.status = FallStatus.CANCELLED
                event.resolved_at = datetime.now(timezone.utc)
                event.meta_data = '{"trigger": "USER_CANCEL"}'
                await db.commit()
                await sos_service.send_safe_sms(db, event)

    async def _do_manual_sos(self, event_uid: uuid.UUID):
        async with self._get_new_session() as db:
            res = await db.execute(select(FallEvent).where(FallEvent.event_uid == event_uid))
            event = res.scalar_one_or_none()
            if event and event.status == FallStatus.PENDING:
                event.status = FallStatus.CONFIRMED
                event.resolved_at = datetime.now(timezone.utc)
                event.meta_data = '{"trigger": "MANUAL_SOS"}'
                await db.commit()
                await sos_service.execute_sos_protocol(db, event)
                self._start_location_updates(event_uid, event.user_id)

    async def _on_timeout(self, event_uid: uuid.UUID):
        print(f"[FallEngine] TIMEOUT: {event_uid} -> TRIGGERING SOS")
        async with self._get_new_session() as db:
            res = await db.execute(select(FallEvent).where(FallEvent.event_uid == event_uid))
            event = res.scalar_one_or_none()
            if not event or event.status != FallStatus.PENDING:
                return
            event.status = FallStatus.CONFIRMED
            event.resolved_at = datetime.now(timezone.utc)
            event.meta_data = '{"trigger": "TIMEOUT_15S"}'
            await db.commit()
            await sos_service.execute_sos_protocol(db, event)
            self._start_location_updates(event_uid, event.user_id)
        with self._lock:
            self._timers.pop(str(event_uid), None)

    def _start_location_updates(self, event_uid: uuid.UUID, user_id: str):
        def update_loc():
            with self._lock:
                count = self._loc_counts.get(str(event_uid), 0)
                if count >= settings.MAX_LOCATION_UPDATES:
                    self._loc_timers.pop(str(event_uid), None)
                    self._loc_counts.pop(str(event_uid), None)
                    return
                self._loc_counts[str(event_uid)] = count + 1
            print(f"[FallEngine] Location Update #{count+1} for {event_uid}")
            timer = threading.Timer(settings.LOCATION_UPDATE_INTERVAL, update_loc)
            timer.daemon = True
            timer.start()
            with self._lock:
                self._loc_timers[str(event_uid)] = timer
        timer = threading.Timer(settings.LOCATION_UPDATE_INTERVAL, update_loc)
        timer.daemon = True
        timer.start()
        with self._lock:
            self._loc_timers[str(event_uid)] = timer
            self._loc_counts[str(event_uid)] = 0

    def shutdown_all(self):
        with self._lock:
            for t in self._timers.values(): t.cancel()
            for t in self._loc_timers.values(): t.cancel()
            self._timers.clear()
            self._loc_timers.clear()

fall_engine = FallEngine()