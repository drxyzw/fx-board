from dotenv import load_dotenv
import os
import pandas as pd
from fredapi import Fred # for FRED BIS
import sdmx # IMF
import datetime

from utils.config import *

class PrecomputedNeer:
    storeFilename = ""
    def __init__(self, freq):
        pass
    
    def onlyPrecomputed(self, target_period):
        pass

    def getNeerSeries(self, ccies):
        return None

class PrecomputeNeerBis(PrecomputedNeer):
    def __init__(self, freq="M"):
        load_dotenv()
        self.storeFilename = os.getenv("PRECOMPUTED_NEER_STORE_DIR") + "/FRED_BIS_NEER.xlsx"
        self.freq = freq
        return
    
    def onlyPrecomputed(self):
        if self.freq not in ["M"]: # ["A", "M"]:
            return False
        else:
            onlyPrecomputed_bool = all([not(value["FRED"] is None) for value in ccies.values() ])  
            return onlyPrecomputed_bool

    def getNeerSeries(self, ccies):
        fred_bis_api_key = os.getenv("FRED_API_KEY")
        fred = Fred(api_key=fred_bis_api_key)
        NEER_dfs = []
        for ccy, value in ccies.items():
            fred_key = value["BIS"]
            isInclude = value["Include"]
            NEER_country = None
            if isInclude:
                if fred_key is not None:
                    NEER_country = fred.get_series("NB" + fred_key + "BIS").to_frame()
                    print(f'fetched currency {ccy} from web')
                    NEER_country.index.name = "Date"
                    NEER_country.columns = [ccy]
                    NEER_dfs.append(NEER_country)
        NEER_df = pd.concat(NEER_dfs, axis=1)
        NEER_df.to_excel(self.storeFilename, index=True)
        return NEER_df
    
class PrecomputeNeerImf(PrecomputedNeer):
    def __init__(self, freq="M"):
        load_dotenv()
        self.startYear = 2000
        self.freq = freq
        self.storeFilename = os.getenv("PRECOMPUTED_NEER_STORE_DIR") + "/IMF_NEER.xlsx"
        return
    
    def onlyPrecomputed(self):
        if self.freq not in ["A", "M"]:
            return False
        else:
            onlyPrecomputed_bool = all([not(value["IMF"] is None) for value in ccies.values() ])  
            return onlyPrecomputed_bool

    def getNeerSeries(self, ccies):
        IMF_DATA = sdmx.Client('IMF_DATA')
        res_NEER = "EER"

        NEER_dfs = []
        for ccy, value in ccies.items():
            imf_key = value["IMF"]
            key_NEER = f"{imf_key}.NEER_IX_RY2010_ACW.{self.freq}"
            isInclude = value["Include"]
            NEER_country = None
            if isInclude:
                if imf_key is not None:
                    data_msg = IMF_DATA.data(res_NEER, key=key_NEER, params={"startPeriod": self.startYear})
                    print(f'fetched currency {ccy} from web')
                    NEER_country = sdmx.to_pandas(data_msg)
                    NEER_country_flat_index = NEER_country.reset_index()
                    NEER_country_flat_index["Date"] = NEER_country_flat_index['TIME_PERIOD'].apply(lambda x: 
                        pd.to_datetime(x + "-01", format="%Y-M%m-%d")
                    )
                    NEER_country_new_index = NEER_country_flat_index.set_index("Date")[["value"]]
                    NEER_country_new_index.columns = [ccy]
                    NEER_dfs.append(NEER_country_new_index)
        NEER_df = pd.concat(NEER_dfs, axis=1)
        NEER_df.to_excel(self.storeFilename, index=True)
        return NEER_df
    
