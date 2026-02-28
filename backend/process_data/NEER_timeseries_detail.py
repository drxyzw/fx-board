from dotenv import load_dotenv
import os
import shutil
import pandas as pd
import numpy as np
import json

from utils.utils import *
from utils.config import *

load_dotenv()
freq = os.getenv("FX_RATE_FREQ")
freq_label = freqToString(freq)
neer_raw_file = os.getenv("NEER_STORE_DIR") + f"/NEER_DETAIL_{freq_label.upper()}.parquet"
output_csv = False
output_parquet = False
output_json = True

if output_csv:
    neer_chart_detail_file = os.getenv("NEER_CHART_DIR") + f"/NEER_DETAIL_CUMUL_{freq_label.upper()}.csv"
if output_parquet:
    neer_chart_detail_parquet_file = os.getenv("NEER_CHART_DIR") + f"/NEER_DETAIL_CUMUL_{freq_label.upper()}.parquet"
ccy_country_file = os.getenv("NEER_CHART_DIR") + f"/detail/CCY_COUNTRY.json"

# currency and coutnry map
ccy_country_dict = {k: v["IMF_DOTS"] for k, v in ccies.items()}
if "EUR" in ccy_country_dict.keys():
    ccy_country_dict["EUR"] = euro_countries
with open(ccy_country_file, "w") as json_file:
    json.dump(ccy_country_dict, json_file)

# detail file
df = pd.read_parquet(neer_raw_file)
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
df_chart = pd.concat(df_tss).reset_index(drop=False)

if output_csv:
    df_chart.to_csv(neer_chart_detail_file, index=False)
if output_parquet:
    df_chart.to_parquet(neer_chart_detail_parquet_file, compression="zstd", index=False)

if output_json:
    target_dir =  os.getenv("NEER_CHART_DIR") + f"/detail"
    for reporter in df_chart["reporter"].unique():
        df_chart_r = df_chart[df_chart["reporter"] == reporter].replace({np.nan: None})
        dates = sorted(df_chart_r["Date"].unique())
        partner_dict = {}
        for partner in df_chart_r["partner"].unique():
            df_chart_rp = df_chart_r[df_chart_r["partner"] == partner][["Date", "weight", "return", "contribution"]]
            df_chart_rp = df_chart_rp.set_index("Date")
            df_chart_rp = df_chart_rp.reindex(dates)
            df_chart_rp = df_chart_rp.ffill().fillna(0.)
            partner_dict[partner] = {
                        "cum_weight": df_chart_rp["weight"].cumsum().to_list(),
                        "return": df_chart_rp["return"].to_list(),
                        "contribution": df_chart_rp["contribution"].to_list(),
                    }
        df_dict = {
            "Date": sorted(df_chart_r["Date"].astype("str").unique()),
            "partner": partner_dict,
        }
        target_file = target_dir + f"/{reporter}.json"
        with open(target_file, "w") as json_file:
            json.dump(df_dict, json_file)
    fronend_dir = os.getenv("FRONTEND_DATA_DIR") + "/detail"
    os.makedirs(fronend_dir, exist_ok=True)
    shutil.copytree(target_dir, fronend_dir, dirs_exist_ok=True)

