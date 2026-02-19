from dotenv import load_dotenv
import os
import requests
from requests.exceptions import RequestException
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from datetime import timedelta

from utils.config import *
from utils.utils import *


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
        freq_label = freqToString(self.freq)
        self.storeFilename = os.getenv("FX_RATE_DATA_STORE_DIR") + f"/BIS_FX_RATE_DATA_{freq_label.upper()}.csv"
        self.startDate=os.getenv("FX_START_DATE")
        self.endDate=os.getenv("FX_END_DATE")
        return
    
    def getFxSeries(self, ccies, loadFileIfExists):
        if loadFileIfExists and os.path.exists(self.storeFilename):
            fx_df = pd.read_csv(self.storeFilename, index_col = "Date")
            fx_df.index = pd.to_datetime(fx_df.index)
        else:
            fx_dfs = []
            fx_not_in_bis = []
            fx_df_fallback = None
            base_url = "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/"
            ccies_columns = []
            for ccy, ccy_value in ccies.items():
                ccies_columns.append(ccy)
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
                                    date_str = obs.attrib.get("TIME_PERIOD")
                                    value = obs.attrib.get("OBS_VALUE")
                                    if value != "NaN":
                                        if self.freq == "D":
                                            date = pd.to_datetime(date_str, format="%Y-%m-%d")
                                        elif self.freq == "M":
                                            date = pd.to_datetime(date_str + "-01", format="%Y-%m-%d")
                                        elif self.freq == "A":
                                            date = pd.to_datetime(date_str + "-01-01", format="%Y-%m-%d")
                                        else:
                                            raise ValueError("Invalid freq: " + self.freq)
                                        data_ccy_dict.append({"Date": date, ccy: value})
                        data_ccy = pd.DataFrame(data_ccy_dict)
                        data_ccy.set_index("Date", inplace=True)
                        fx_dfs.append(data_ccy)
                        print(f"BIS {ccy} FX rate is imported.")
                        fx_df = pd.concat(fx_dfs, axis=1)
                    else:
                        fx_not_in_bis.append(ccy)
            # for fx not in BIS data, we take from exhangerate.host as a fallback
            if len(fx_not_in_bis) > 0:
                fallback_base_url = "https://api.exchangerate.host/timeframe"
                exchangerate_host_api_key = os.getenv("EXCHANGERATE_HOST_API_KEY")
                pairs = ",".join(set(fx_not_in_bis + ["USD"]))
                # maximum time window is 365 days, so we divide
                startDate = datetime.strptime(self.startDate, "%Y-%m-%d")
                endDate = datetime.strptime(self.endDate, "%Y-%m-%d")
                startDate_inc = startDate
                fx_df_fallback_incs = []
                while startDate_inc < endDate:
                    endDate_inc = min(endDate, startDate_inc + timedelta(days=364))
                    params = {
                        "access_key": exchangerate_host_api_key,
                        "start_date": datetime.strftime(startDate_inc, "%Y-%m-%d"),
                        "end_date": datetime.strftime(endDate_inc, "%Y-%m-%d"),
                        "currencies": pairs,
                    }
                    fallback_res = requests.get(fallback_base_url, params=params)
                    status_code = fallback_res.status_code
                    fallback_data = fallback_res.json()
                    if status_code == 200:
                        quotes = fallback_data["quotes"]
                        quotes_clean = {k: (v if isinstance(v, dict) else {}) for k, v in quotes.items()} # replacing [] with {}, otherwise error
                        fx_df_fallback_inc = pd.DataFrame(quotes_clean).T
                        fx_df_fallback_incs.append(fx_df_fallback_inc)
                    else:
                        error_dict = fallback_data["error"]
                        error_code = error_dict["code"]
                        error_type = None if "type" not in error_dict.keys() else error_dict["type"]
                        error_info = error_dict["info"]
                        if error_code == 106: # 'type': 'no_rates_available', 'info': 'Your query did not return any results. Please try again.'
                            pass
                        else:
                            if error_type:
                                raise RequestException(f"Exchangerate.host request failed: status code: {status_code}, type: {error_type}, info: {error_info}")
                            else:
                                raise RequestException(f"Exchangerate.host request failed: status code: {status_code}, info: {error_info}")
                    startDate_inc = endDate_inc + timedelta(days=1)
                fx_df_fallback = pd.concat(fx_df_fallback_incs)
                print(",".join(fx_not_in_bis) + "loaded from Exchangerate.host as a fallback")
            if not fx_df_fallback is None:
                fx_df_fallback.columns = [c[3:] for c in fx_df_fallback.columns] # columns "USDXXX" --> "XXX"
                fx_df_fallback.index = pd.to_datetime(fx_df_fallback.index)
                fx_df = fx_df.join(fx_df_fallback)
                fx_df = fx_df[ccies_columns]
            fx_df.to_csv(self.storeFilename, index=True)
        return fx_df

