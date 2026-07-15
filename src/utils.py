import os
from datetime import datetime
import numpy as np

def make_feature_row(timestamp_iso: str, temp_c: float) -> dict:
    # Handle timezone-aware parsing safely in Python 3.11+ (Z and offset)
    val = timestamp_iso.replace("Z", "+00:00")
    dt = datetime.fromisoformat(val)
    
    # Extract features using local time of the timestamp to avoid timezone drift
    return {
        "hour": int(dt.hour),
        "dayofweek": int(dt.weekday()),  # 0 is Monday, 6 is Sunday (matches pandas)
        "month": int(dt.month),
        "temp_c": float(temp_c)
    }

class SecureMLPRegressor:
    """
    Secure, lightweight forward pass for MLPRegressor.
    Eliminates dependency on scikit-learn/joblib and mitigates Pickle RCE risk.
    """
    def __init__(self, weights_path: str):
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Model weights file not found at: {weights_path}")
            
        data = np.load(weights_path)
        self.w1 = data["w1"]
        self.b1 = data["b1"]
        self.w2 = data["w2"]
        self.b2 = data["b2"]
        self.w3 = data["w3"]
        self.b3 = data["b3"]

    def predict(self, X: list) -> list:
        # X is a 2D list-like input of shape (n_samples, 4)
        x_arr = np.array(X, dtype=np.float32)
        
        # Layer 1: ReLU(X @ W1 + b1)
        h1 = np.maximum(0.0, np.dot(x_arr, self.w1) + self.b1)
        # Layer 2: ReLU(h1 @ W2 + b2)
        h2 = np.maximum(0.0, np.dot(h1, self.w2) + self.b2)
        # Layer 3: Linear/Identity(h2 @ W3 + b3)
        y = np.dot(h2, self.w3) + self.b3
        
        # Return as list of floats to preserve scikit-learn API compatibility
        return y.flatten().tolist()
