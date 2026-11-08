import threading
import numpy as np
import onnxruntime as ort
import joblib
from pathlib import Path
from collections import deque
from typing import List, Dict, Optional
from app.config import settings
from app.models.pydantic_schemas import SensorReading

class ModelService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        self.session: Optional[ort.InferenceSession] = None
        self.scaler = None
        self.input_name = None
        self.output_name = None
        self.window_size = settings.MODEL_WINDOW_SIZE
        self.feature_count = 6
        self.threshold = settings.MODEL_THRESHOLD
        
        self._buffers: Dict[str, deque] = {}
        self._buffer_lock = threading.Lock()
        self._load_artifacts()

    def _load_artifacts(self):
        if settings.MODEL_PATH.exists():
            print(f"[ModelService] Loading ONNX: {settings.MODEL_PATH}")
            self.session = ort.InferenceSession(str(settings.MODEL_PATH), providers=['CPUExecutionProvider'])
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
        else:
            print(f"[ModelService] WARNING: Model not found. MOCK MODE.")

        if settings.SCALER_PATH.exists():
            self.scaler = joblib.load(settings.SCALER_PATH)
            print("[ModelService] Scaler loaded.")

    def process_batch(self, device_id: str, readings: List[SensorReading]) -> List[Dict]:
        results = []
        with self._buffer_lock:
            if device_id not in self._buffers:
                self._buffers[device_id] = deque(maxlen=self.window_size)
            buf = self._buffers[device_id]

            for r in readings:
                features = [r.acc_x, r.acc_y, r.acc_z, r.gyro_x, r.gyro_y, r.gyro_z]
                buf.append(features)

                if len(buf) == self.window_size:
                    window_array = np.array(buf, dtype=np.float32).reshape(1, self.window_size, self.feature_count)
                    result = self._predict(window_array)
                    result['device_id'] = device_id
                    result['timestamp'] = r.timestamp
                    result['gps_lat'] = r.gps_lat
                    result['gps_lon'] = r.gps_lon
                    results.append(result)

                    if result['is_fall']:
                        buf.clear() # Cooldown
        return results

    def _predict(self, window_array: np.ndarray) -> Dict:
        if not self.session:
            is_fall = np.random.random() < 0.005 
            return {"probability": 0.95 if is_fall else 0.05, "label": 1 if is_fall else 0, "is_fall": is_fall, "threshold": self.threshold}

        x = window_array.copy()
        if self.scaler:
            orig_shape = x.shape
            x_flat = x.reshape(-1, self.feature_count)
            x_flat = self.scaler.transform(x_flat)
            x = x_flat.reshape(orig_shape)

        outputs = self.session.run([self.output_name], {self.input_name: x})
        logits = outputs[0][0]
        
        if len(logits) > 1:
            prob = float(1 / (1 + np.exp(-logits[1])))
        else:
            prob = float(1 / (1 + np.exp(-logits[0])))
            
        label = 1 if prob > self.threshold else 0
        return {"probability": round(prob, 4), "label": label, "is_fall": bool(label == 1), "threshold": self.threshold}

    def reset_buffer(self, device_id: str):
        with self._buffer_lock:
            if device_id in self._buffers:
                self._buffers[device_id].clear()

model_service = ModelService()