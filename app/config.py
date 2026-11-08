from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://pilot:pilot123@localhost:5432/safelife"
    API_KEY: str = "pilot-secret-key-123"
    ENV: str = "development"

    # Database Engine Config
    DB_ECHO: bool = False  # <--- BUNU ƏLAVƏ EDİN (True olarsa SQL logları çıxar)

    # Model Config
    MODEL_PATH: Path = Path("models/best_model.onnx")
    SCALER_PATH: Path = Path("models/scaler.joblib")
    MODEL_WINDOW_SIZE: int = 100
    MODEL_THRESHOLD: float = 0.55

    # SOS Config
    SOS_TIMEOUT_SECONDS: int = 15
    LOCATION_UPDATE_INTERVAL: int = 30
    MAX_LOCATION_UPDATES: int = 40

    class Config:
        env_file = "../.env"  # Kök qovluqdakı .env
        extra = "ignore"

settings = Settings()