from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.model_service import model_service
from app.models.pydantic_schemas import HealthResponse  # <--- Sizin faylınızdan import

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
async def health_check(db = Depends(get_db)):
    try:
        await db.execute("SELECT 1")
        db_ok = True
    except:
        db_ok = False
    
    model_ok = model_service.session is not None
    
    return HealthResponse(
        status="ok" if db_ok else "degraded",
        database="connected" if db_ok else "disconnected",
        ai_model_loaded=model_ok,  
        threshold=model_service.threshold
    )
