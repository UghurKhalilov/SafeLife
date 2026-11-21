from fastapi import APIRouter, HTTPException, status
from pathlib import Path
import csv
import time
from datetime import datetime, timezone

from app.models.pydantic_schemas import (
    CollectPayload,
    CollectResponse,
    CollectLabel,
)

router = APIRouter(prefix="/api/v1", tags=["Collect"])

# Data collection directory
COLLECT_DIR = Path("data/collected")


@router.post("/collect", response_model=CollectResponse)
async def collect_training_data(payload: CollectPayload):
    """
    Collect labeled sensor data for model training.

    Accepts a batch of sensor samples with a label (walk, run, phone_drop, fall, crash_sim).
    Saves each batch to a CSV file under data/collected/.
    """
    # Ensure collection directory exists
    COLLECT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate filename: {device_id}_{session_id}_{label}_{timestamp}.csv
    timestamp = int(time.time() * 1000)  # milliseconds
    label_str = payload.label.value
    filename = f"{payload.device_id}_{payload.session_id}_{label_str}_{timestamp}.csv"
    file_path = COLLECT_DIR / filename

    # Write CSV
    try:
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            # Header
            writer.writerow([
                "timestamp", "ax", "ay", "az", "gx", "gy", "gz",
                "speed", "latitude", "longitude",
                "device_id", "session_id", "label"
            ])
            # Data rows
            for sample in payload.samples:
                writer.writerow([
                    sample.timestamp,
                    sample.ax, sample.ay, sample.az,
                    sample.gx, sample.gy, sample.gz,
                    sample.speed,
                    sample.latitude, sample.longitude,
                    payload.device_id,
                    payload.session_id,
                    label_str
                ])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write CSV: {str(e)}"
        )

    return CollectResponse(
        file_path=str(file_path),
        sample_count=len(payload.samples),
        message=f"Saved {len(payload.samples)} samples to {filename}"
    )