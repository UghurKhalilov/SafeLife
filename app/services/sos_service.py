from typing import List
from sqlalchemy.orm import Session
from app.models.db_models import User, TrustedContact, FallEvent
from app.config import settings

class SosService:
    def send_sms(self, to_phone: str, text: str) -> bool:
        print(f"[SOS SMS] TO: {to_phone} | TEXT: {text[:50]}...")
        # REAL: Twilio client.messages.create(...)
        return True

    def make_call(self, to_phone: str) -> bool:
        print(f"[SOS CALL] CALLING: {to_phone}")
        # REAL: Twilio client.calls.create(...)
        return True

    def execute_sos_protocol(self, db: Session, event: FallEvent):
        user = db.query(User).filter(User.id == event.user_id).first()
        if not user: return

        contacts: List[TrustedContact] = [c for c in user.contacts if c.is_active][:5]
        medical = user.medical_info or "Məlumat yoxdur"
        loc = f"https://maps.google.com/?q={event.gps_lat},{event.gps_lon}" if event.gps_lat else "Lokasiya yoxdur"
        
        sms_text = (
            f"[SAFELIFE QƏZA] İstifadəçi: {user.username}\n"
            f"Ehtimal: %{event.probability*100:.0f}\n"
            f"Lokasiya: {loc}\n"
            f"Tibbi: {medical}\n"
            f"Vaxt: {event.triggered_at.strftime('%H:%M:%S')}"
        )

        for c in contacts:
            self.send_sms(c.phone, sms_text)
        
        self.make_call("103")
        print(f"[SosService] SOS Protocol executed for {event.event_uid}")

    def send_safe_sms(self, db: Session, event: FallEvent):
        user = db.query(User).filter(User.id == event.user_id).first()
        if not user: return
        contacts = [c for c in user.contacts if c.is_active][:5]
        text = f"[SAFELIFE TƏHLÜKƏSİZDIR] {user.username} 'Mən yaxşıyam' düyməsini bastı. Qəza ləğv edildi."
        for c in contacts:
            self.send_sms(c.phone, text)

sos_service = SosService()