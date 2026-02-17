from dotenv import load_dotenv
import os
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from utils.config import *

class FXRateData:
    storeFilename = ""
    freq = ""
    def __init__(self):
        load_dotenv()
        self.freq = os.getenv("FX_RATE_FREQ")
    
    def getFxSeries(self, ccies, loadFileIfExists):
        return None

class BisFXRateData(FXRateData):
    startDate = ""
    endDate = ""
    def __init__(self):
        super().__init__()
        self.storeFilename = os.getenv("FX_RATE_DATA_STORE_DIR") + "/BIS_FX_RATE_DATA.csv"
        self.startDate=os.getenv("FX_START_DATE")
        self.endDate=os.getenv("FX_END_DATE")
        return
    
    def getFxSeries(self, ccies, loadFileIfExists):
        if loadFileIfExists and os.path.exists(self.storeFilename):
            fx_df = pd.read_excel(self.storeFilename, index_col = "Date")
        else:
            fx_dfs = []
            base_url = "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/"
            for ccy, ccy_value in ccies.items():
                bis_key = ccy_value["BIS_FX"]
                isInclude = ccy_value["Include"]
                if isInclude:
                    if bis_key is not None:
                        url = (
                            f"{base_url}"
                            f"{self.freq}.{bis_key}.{ccy}"
                            f".A?startPeriod={self.startDate}&endPeriod={self.endDate}&format=sdmx-compact-2.0"
                        )
                        data = requests.get(url).content
                        # parse SDMX
                        # pandsmdx is not useful because it is not compatible with python 3.13
                        root = ET.fromstring(data)
                        data_ccy_dict = []
                        for series in root.findall(".//ns1:Series", ns):
                            for obs in series.findall("ns1:Obs", ns):
                                    date = obs.attrib.get("TIME_PERIOD")
                                    value = obs.attrib.get("OBS_VALUE")
                                    if value != "NaN":
                                        data_ccy_dict.append({"Date": pd.to_datetime(date, format="%Y-%m-%d"), ccy: value})
                        data_ccy = pd.DataFrame(data_ccy_dict)
                        data_ccy.set_index("Date", inplace=True)
                        fx_dfs.append(data_ccy)
                        print(f"BIS {ccy} FX rate is imported.")
                        fx_df = pd.concat(fx_dfs, axis=1)
            fx_df.to_csv(self.storeFilename, index=True)
        return None

