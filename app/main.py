from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
# Yalnız mövcud router-ləri import et
from app.api import routes_health, routes_ingest


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("SafeLife Pilot Server Starting...")
    await init_db() 
    print("Database initialized.")
    yield
    print("Shutting down... Cancelling timers.")
    # fall_engine.shutdown_all()  # <<< KOMMENT ET (hələ yoxdur)

app = FastAPI(
    title="SafeLife Pilot API",
    version="2.0.0-modular-async",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(routes_health.router)
app.include_router(routes_ingest.router)


@app.get("/")
def root():
    return {"service": "SafeLife Pilot API", "docs": "/docs"}