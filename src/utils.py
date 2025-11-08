
from datetime import datetime
import pandas as pd

def make_feature_row(timestamp_iso: str, temp_c: float):
    ts = pd.to_datetime(timestamp_iso, utc=True)
    row = {
        "hour": int(ts.hour),
        "dayofweek": int(ts.dayofweek),
        "month": int(ts.month),
        "temp_c": float(temp_c)
    }
    return row
