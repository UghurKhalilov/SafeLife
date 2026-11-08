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
    
    # Hər user/device üçün ayrı buffer (Sliding Window)
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
        self.window_size: int = settings.MODEL_WINDOW_SIZE  # Məs: 100 (2s @ 50Hz)
        self.feature_count: int = 6  # acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z
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
            # Model input shape: [Batch, Window, Features] və ya [Batch, Features]
            # Biz [1, Window, 6] dəyərləyirik.
        else:
            print(f"[ModelService] WARNING: Model not found at {model_path}. Running in MOCK mode.")

        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)
            print("[ModelService] Scaler loaded.")
        else:
            print("[ModelService] WARNING: Scaler not found. Raw features will be used.")

    def add_sample(self, device_id: str, features: List[float]) -> Optional[np.ndarray]:
        """
        Yeni sample əlavə et. Buffer dolarsa (window_size), model input array qaytar.
        Hələ dolmayıbsa None qaytar.
        """
        if len(features) != self.feature_count:
            raise ValueError(f"Expected {self.feature_count} features, got {len(features)}")

        with self._buffer_lock:
            if device_id not in self._buffers:
                self._buffers[device_id] = deque(maxlen=self.window_size)
            
            buf = self._buffers[device_id]
            buf.append(features)
            
            if len(buf) == self.window_size:
                # Buffer doldu -> Predict üçün array hazırla [1, Window, Features]
                return np.array(buf, dtype=np.float32).reshape(1, self.window_size, self.feature_count)
        
        return None

    def predict(self, window_array: np.ndarray) -> Dict:
        """
        Model predict. window_array shape: [1, Window, Features]
        """
        if not self.session:
            # Mock response for demo
            return {"probability": 0.05, "label": 0, "threshold": 0.5, "is_fall": False}

        x = window_array.copy()
        
        # Scaler tətbiq et (Flatten -> Scale -> Reshape back)
        if self.scaler:
            orig_shape = x.shape
            x_flat = x.reshape(-1, self.feature_count)
            x_flat = self.scaler.transform(x_flat)
            x = x_flat.reshape(orig_shape)

        # ONNX Run
        outputs = self.session.run([self.output_name], {self.input_name: x})
        
        # Output formatı modelə görə dəyişir. Burada binary classification [prob_class_0, prob_class_1] varsayıb.
        logits = outputs[0][0]  # Shape: [2] və ya [1]
        
        if len(logits) > 1:
            prob = float(1 / (1 + np.exp(-logits[1])))  # Sigmoid for logit 1
        else:
            prob = float(1 / (1 + np.exp(-logits[0])))

        label = 1 if prob > 0.5 else 0
        
        return {
            "probability": round(prob, 4),
            "label": label,
            "threshold": 0.5,
            "is_fall": bool(label == 1)
        }

    def reset_buffer(self, device_id: str):
        """Qəza aşkarlananda buffer-i sıfırla (cooldown)."""
        with self._buffer_lock:
            if device_id in self._buffers:
                self._buffers[device_id].clear()

model_service = ModelService()