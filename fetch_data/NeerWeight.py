from dotenv import load_dotenv
import pandas as pd
import os
from dateutil.relativedelta import relativedelta
import numpy as np

from utils.utils import *

class NeerWeight:
    tradeData = ""
    storeFilename = ""
    freq = ""
    minWeightCutoff = 0.0
    def __init__(self, tradeData):
        load_dotenv()
        self.tradeData = tradeData
        self.minWeightCutoff = float(os.getenv("WEIGHT_CUTOFF"))
    def computeWeight(self):
        pass

class ImfNeerWeight(NeerWeight):
    def __init__(self, tradeData):
        super().__init__(tradeData=tradeData)
        self.freq = os.getenv("TRADE_FREQ")
        freq_label = freqToString(self.freq)
        self.storeFilename = os.getenv("TRADE_DATA_STORE_DIR") + f"/imf_dots_weight_{freq_label.lower()}.csv"
    def computeWeight(self, loadFileIfExists):
        if loadFileIfExists and os.path.exists(self.storeFilename):
            df_trade = pd.read_csv(self.storeFilename, index_col = "Date")
            df_trade.index = pd.to_datetime(df_trade.index)
        else:
            df_trade = pd.pivot_table(
                self.tradeData,
                index=["Date", "reporter", "partner"],
                columns="indicator",
                values="value")
            df_trade = df_trade.reset_index()
            df_trade["import_export"] = df_trade["XG_FOB_USD"] + df_trade["MG_CIF_USD"]
            df_trade = df_trade[["Date", "reporter", "partner", "import_export"]]
            # if import_export is nan, use a mirror value ("reporter" and "partner" are swapped)
            df_mirror = df_trade.rename(columns={"reporter": "partner", "partner": "reporter", "import_export": "import_export_mirror"})
            df_trade = df_trade.merge(df_mirror, on=["Date", "reporter", "partner"], how="left")
            df_trade["import_export"] = df_trade["import_export"].fillna(df_trade["import_export_mirror"])
            df_trade = df_trade[["Date", "reporter", "partner", "import_export"]]
            # ratio among all parter countries
            df_trade["weight"] = df_trade["import_export"] / df_trade.groupby(["Date", "reporter"])["import_export"].transform("sum")
            # if weight < minWeightCutOff, impute it as 0, then renormalize
            df_trade["weight"] = np.where(df_trade["weight"] < self.minWeightCutoff, 0.0, df_trade["weight"])
            df_trade["weight"] = df_trade["weight"] / df_trade.groupby(["Date", "reporter"])["weight"].transform("sum")
            # sum_one = df_trade.groupby(["Date", "reporter"])["weight"].transform("sum")
            df_trade = df_trade[["Date", "reporter", "partner", "weight"]]
            df_trade = pd.pivot_table(
                df_trade,
                index=["Date", "reporter"],
                columns="partner",
                values="weight")
            df_trade = df_trade.reset_index().sort_values(["reporter", "Date"])
            partner_cols = df_trade.columns.difference(["reporter", "Date"]) # extract columns (currencies) other than "reporter", "Date"
            freq_factor = 0
            if self.freq == "A":
                freq_factor = 1
            elif self.freq == "M":
                freq_factor = 12
            else:
                raise ValueError("Trade data only supports frequency of annually or monthly, but frequency is: " + self.freq)
            df_trade[partner_cols] = df_trade.groupby("reporter")[partner_cols].transform(
                lambda x: x.rolling(window=3*freq_factor, min_periods=1).mean()
            )
            df_trade = pd.melt(df_trade,
                               id_vars=["Date", "reporter"],
                               var_name="partner",
                               value_name="weight")
            # because the moving average of partially missing value distorts normalization,
            # renormalizatoin is required
            df_trade["weight"] = df_trade["weight"] / df_trade.groupby(["Date", "reporter"])["weight"].transform("sum")
            df_trade = df_trade.dropna().reset_index()
            df_trade = df_trade.set_index("Date")
            df_trade = df_trade[["reporter", "partner", "weight"]]
            df_trade.to_csv(self.storeFilename)
        return df_trade
        
