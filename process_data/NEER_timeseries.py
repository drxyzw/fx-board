from dotenv import load_dotenv
import os
import pandas as pd

from utils.utils import *

load_dotenv()
freq = os.getenv("FX_RATE_FREQ")
freq_label = freqToString(freq)
neer_raw_file = storeFilename = os.getenv("NEER_STORE_DIR") + f"/NEER_{freq_label.upper()}.csv"
neer_chart_file = storeFilename = os.getenv("NEER_CHART_DIR") + f"/NEER_CHART_{freq_label.upper()}.csv"

df = pd.read_csv(neer_raw_file)
# impute missing value with previous day's value
df_imputed = df.ffill().dropna()
# convert to flatten form
df_flat = pd.melt(df_imputed, id_vars=["Date"], var_name="Currency", value_name="NEER")
df_flat.to_csv(neer_chart_file, index=False)
