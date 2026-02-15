from dotenv import load_dotenv
import os
import pandas as pd
from fredapi import Fred

from utils.config import *

class PrecomputedNeer:
    storeFilename = ""
    def __init__(self):
        pass
    
    def onlyPrecomputed(self, target_period):
        pass

    def getNeerSeries(self, ccies):
        return None

class PrecomputeNeerBis(PrecomputedNeer):
    def __init__(self):
        load_dotenv()
        self.storeFilename = os.getenv("PRECOMPUTED_NEER_STORE_DIR") + "/"
        return
    
    def onlyPrecomputed(self, target_period):
        if target_period not in ["A", "M"]:
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
                    NEER_country.columns = [ccy]
                    NEER_dfs.append(NEER_country)
        NEER_df = pd.concat(NEER_dfs, axis=1)
        return NEER_df
    
