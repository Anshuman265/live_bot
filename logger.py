import pandas as pd
from config import LOG_PATH

def append_log(row: dict):
    try:
        df = pd.DataFrame([row])
        header = not pd.io.common.file_exists(LOG_PATH)
        df.to_csv(LOG_PATH, mode="a", index=False, header=header)
    except Exception as e:
        print(f"[WARN] failed to log: {e}")