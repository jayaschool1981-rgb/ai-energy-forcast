
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error

from .data_prep import load_data
from .feature_engineering import add_calendar_features, select_feature_columns

def evaluate_model(csv_path: str, model_path: str) -> dict:
    df = load_data(csv_path)
    df = add_calendar_features(df)
    feature_cols = select_feature_columns()
    X = df[feature_cols].values
    y = df["energy_kwh"].values

    split = int(len(df)*0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = joblib.load(model_path)
    preds = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, preds))
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    mape = float(np.mean(np.abs((y_test - preds)/(y_test+1e-6)))*100.0)
    return {"mae": mae, "rmse": rmse, "mape": mape}
