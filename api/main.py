from fastapi import FastAPI
from pydantic import BaseModel, Field
import joblib
import os
from src.utils import make_feature_row
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Energy Forecasting API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "energy_mlp.pkl")
model = joblib.load(MODEL_PATH)

class PredictIn(BaseModel):
    timestamp: str = Field(..., description="ISO timestamp e.g. 2025-11-08T14:00:00Z")
    temp_c: float = Field(..., description="Temperature in Celsius")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(inp: PredictIn):
    row = make_feature_row(inp.timestamp, inp.temp_c)
    X = [[row["hour"], row["dayofweek"], row["month"], row["temp_c"]]]
    yhat = model.predict(X)[0]
    return {
        "timestamp": inp.timestamp,
        "temp_c": inp.temp_c,
        "predicted_kwh": float(yhat)
    }
