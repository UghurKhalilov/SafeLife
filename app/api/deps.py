from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db

async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
    return x_api_key

# Re-export
get_db = get_db