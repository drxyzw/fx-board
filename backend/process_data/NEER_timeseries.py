from dotenv import load_dotenv
import os
import shutil
import pandas as pd
import numpy as np
import json

from utils.utils import *

load_dotenv()
output_csv = False
output_json = True

freq = os.getenv("FX_RATE_FREQ")
freq_label = freqToString(freq)
neer_raw_file = os.getenv("NEER_STORE_DIR") + f"/NEER_{freq_label.upper()}.csv"
neer_chart_file = os.getenv("NEER_CHART_DIR") + f"/NEER_CHART_{freq_label.upper()}.csv"
neer_chart_json_file = os.getenv("NEER_CHART_DIR") + f"/NEER_CHART_{freq_label.upper()}.json"

df = pd.read_csv(neer_raw_file)
# impute missing value with previous day's value
df_imputed = df.ffill().dropna()
# convert to flatten form
df_flat = pd.melt(df_imputed, id_vars=["Date"], var_name="Currency", value_name="NEER")


if output_csv:
    df_flat.to_csv(neer_chart_file, index=False)

if output_json:
    df_none = df_imputed.replace({np.nan: None})
    df_dict = df_none.to_dict("list")
    with open(neer_chart_json_file, "w") as json_file:
        json.dump(df_dict, json_file)
    shutil.copy(neer_chart_json_file, os.getenv("FRONTEND_DATA_DIR"))

