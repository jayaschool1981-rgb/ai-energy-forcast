
import pandas as pd

def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    # ensure hourly frequency and sort
    df = df.sort_values("timestamp").reset_index(drop=True)
    # forward/backward fill temp if needed
    df["temp_c"] = df["temp_c"].interpolate().bfill().ffill()
    return df
