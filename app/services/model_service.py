import onnxruntime as ort
import numpy as np
import joblib
import threading
from pathlib import Path
from app.config import settings
from collections import deque
from typing import List, Dict, Optional

class ModelService:
    _instance = None
    _lock = threading.Lock()
    
    # Class variables (indent 4 spaces)
    _buffers: Dict[str, deque] = {}
    _buffer_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ModelService, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.session: Optional[ort.InferenceSession] = None
        self.scaler = None
        self.input_name: Optional[str] = None
        self.output_name: Optional[str] = None
        self.window_size: int = settings.MODEL_WINDOW_SIZE
        self.feature_count: int = 6
        
        # THRESHOLD BURADA OLMALIDIR (indent 8 spaces)
        self.threshold: float = settings.MODEL_THRESHOLD
        
        self._load_artifacts()
        self._initialized = True

    def _load_artifacts(self):
        model_path = Path(settings.MODEL_PATH)
        scaler_path = Path(settings.SCALER_PATH)

        if model_path.exists():
            print(f"[ModelService] Loading ONNX model: {model_path}")
            self.session = ort.InferenceSession(str(model_path), providers=['CPUExecutionProvider'])
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
        else:
            print(f"[ModelService] WARNING: Model not found at {model_path}. Running in MOCK mode.")

        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
            print("[ModelService] Scaler loaded.")
        else:
            print("[ModelService] WARNING: Scaler not found. Raw features will be used.")

    def add_sample(self, device_id: str, features: List[float]) -> Optional[np.ndarray]:
        if len(features) != self.feature_count:
            raise ValueError(f"Expected {self.feature_count} features, got {len(features)}")

        with self._buffer_lock:
            if device_id not in self._buffers:
                self._buffers[device_id] = deque(maxlen=self.window_size)
            
            buf = self._buffers[device_id]
            buf.append(features)
            
            if len(buf) == self.window_size:
                return np.array(buf, dtype=np.float32).reshape(1, self.window_size, self.feature_count)
        
        return None

    def predict(self, window_array: np.ndarray) -> Dict:
        if not self.session:
            return {"probability": 0.05, "label": 0, "threshold": self.threshold, "is_fall": False}

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
        
        return {
            "probability": round(prob, 4),
            "label": label,
            "threshold": self.threshold,
            "is_fall": bool(label == 1)
        }

    def reset_buffer(self, device_id: str):
        with self._buffer_lock:
            if device_id in self._buffers:
                self._buffers[device_id].clear()


model_service = ModelService()