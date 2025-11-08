
from typing import Tuple
import pandas as pd
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
import joblib

from .data_prep import load_data
from .feature_engineering import add_calendar_features, select_feature_columns

def train_mlp(csv_path: str, model_out: str) -> dict:
    df = load_data(csv_path)
    df = add_calendar_features(df)
    feature_cols = select_feature_columns()
    X = df[feature_cols].values
    y = df["energy_kwh"].values

    # Time-aware split: last 20% for test
    n = len(df)
    split = int(n*0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = MLPRegressor(hidden_layer_sizes=(64, 64), activation="relu",
                         random_state=42, max_iter=400)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = float(np.mean(np.abs(y_test - preds)))
    rmse = float(np.sqrt(np.mean((y_test - preds)**2)))
    mape = float(np.mean(np.abs((y_test - preds)/(y_test+1e-6)))*100.0)

    joblib.dump(model, model_out)

    return {"mae": mae, "rmse": rmse, "mape": mape}
