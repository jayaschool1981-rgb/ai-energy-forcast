
import pandas as pd

CALENDAR_COLS = ["hour", "dayofweek", "month"]

def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    ts = pd.to_datetime(df["timestamp"], utc=True)
    df["hour"] = ts.dt.hour
    df["dayofweek"] = ts.dt.dayofweek
    df["month"] = ts.dt.month
    return df

def select_feature_columns() -> list:
    return ["hour", "dayofweek", "month", "temp_c"]
