
# Optional LSTM training (exports .h5). Requires tensorflow / keras.
from typing import Tuple
import numpy as np
import pandas as pd
from tensorflow import keras
from tensorflow.keras import layers

from .data_prep import load_data
from .feature_engineering import add_calendar_features, select_feature_columns

def _make_sequences(X: np.ndarray, y: np.ndarray, seq_len: int) -> Tuple[np.ndarray, np.ndarray]:
    xs, ys = [], []
    for i in range(len(X) - seq_len):
        xs.append(X[i:i+seq_len])
        ys.append(y[i+seq_len])
    return np.array(xs), np.array(ys)

def train_lstm(csv_path: str, model_out: str, seq_len: int = 24):
    df = load_data(csv_path)
    df = add_calendar_features(df)
    feature_cols = select_feature_columns()
    X = df[feature_cols].values.astype("float32")
    y = df["energy_kwh"].values.astype("float32")

    # Normalize features
    X_mean, X_std = X.mean(axis=0), X.std(axis=0) + 1e-6
    Xn = (X - X_mean) / X_std

    split = int(len(Xn)*0.8)
    X_train, X_test = Xn[:split], Xn[split:]
    y_train, y_test = y[:split], y[split:]

    Xs_train, ys_train = _make_sequences(X_train, y_train, seq_len)
    Xs_test, ys_test = _make_sequences(X_test, y_test, seq_len)

    model = keras.Sequential([
        layers.Input(shape=(seq_len, Xs_train.shape[-1])),
        layers.LSTM(64, return_sequences=False),
        layers.Dense(32, activation="relu"),
        layers.Dense(1)
    ])
    model.compile(optimizer="adam", loss="mse")
    model.fit(Xs_train, ys_train, epochs=5, batch_size=64, verbose=0)  # small epochs for demo
    test_loss = float(model.evaluate(Xs_test, ys_test, verbose=0))

    model.save(model_out)
    return {"test_mse": test_loss, "note": "LSTM demo trained with few epochs for speed."}
