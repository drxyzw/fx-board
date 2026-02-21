from dotenv import load_dotenv
import os
import pandas as pd

from utils.utils import *

load_dotenv()
freq = os.getenv("FX_RATE_FREQ")
freq_label = freqToString(freq)
neer_raw_file = os.getenv("NEER_STORE_DIR") + f"/NEER_DETAIL_{freq_label.upper()}.csv"
output_csv = False
output_parquet = False

if output_csv:
    neer_chart_detail_file = os.getenv("NEER_CHART_DIR") + f"/NEER_DETAIL_CUMUL_{freq_label.upper()}.csv"
if output_parquet:
    neer_chart_detail_parquet_file = os.getenv("NEER_CHART_DIR") + f"/NEER_DETAIL_CUMUL_{freq_label.upper()}.parquet"

df = pd.read_csv(neer_raw_file)
# impute missing value with previous day's value
df_imputed = df.ffill().dropna()
df_tss = []
for reporter in df_imputed["reporter"].unique():
    df_reporter = df_imputed[df_imputed["reporter"] == reporter]
    for partner in df_reporter["partner"].unique():
        df_ts = df_reporter[df_reporter["partner"] == partner].sort_values(by = "Date")
        df_ts["reporter"] = df_ts["reporter"].astype("category")
        df_ts["partner"] = df_ts["partner"].astype("category")
        df_ts["weight"] = df_ts["weight"].cumsum().astype("float32")
        df_ts["return"] = df_ts["return"].cumsum().astype("float32")
        df_ts["contribution"] = df_ts["contribution"].cumsum().astype("float32")
        df_tss.append(df_ts)
df_chart = pd.concat(df_tss).reset_index(drop=True).rename(columns={"return": "cum_return", "contribution": "cum_contribution"})

if output_csv:
    df_chart.to_csv(neer_chart_detail_file, index=False)
if output_parquet:
    df_chart.to_parquet(neer_chart_detail_parquet_file, compression="zstd", index=False)
