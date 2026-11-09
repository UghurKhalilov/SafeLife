# app/api/routes_health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.api.deps import get_db
from app.services.model_service import model_service
from app.models.pydantic_schemas import HealthResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    # 1. DB yoxlaması
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    
    # 2. Model yoxlaması (defensive coding)
    model_ok = False
    threshold = 0.0
    if model_service and hasattr(model_service, 'session') and model_service.session is not None:
        model_ok = True
        threshold = getattr(model_service, 'threshold', 0.0)
    
    # 3. Status hesabla
    overall_status = "ok" if (db_ok and model_ok) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        database="connected" if db_ok else "disconnected",
        ai_model_loaded=model_ok,
        threshold=threshold
    )