from dotenv import load_dotenv
import os
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from time import sleep

# -----------------------------------------------------------------------------------
class TradeData:
    storeFilename = ""
    freq = ""
    def __init__(self):
        load_dotenv()
        self.freq = os.getenv("TRADE_FREQ")

    def getTradeData(self, ccies):
        pass

# -----------------------------------------------------------------------------------
class ImfDotsTradeData(TradeData):
    def __init__(self, freq="M"):
        super().__init__()
        self.storeFilename = os.getenv("TRADE_DATA_STORE_DIR") + "/imf_dots_trade_data.xlsx"


    def fetchDotsDataframe(self, reporters, partners, indicators, start_period, end_period, freq="M", sleep_sec=1):
        """
        Fetch DOTS data from UK Data Service REST API and return as pandas DataFrame.

        Parameters:
        - reporter: ISO3 code of reporting country (e.g., 'JPN')
        - partner: ISO3 code of partner country (e.g., 'WLD')
        - indicator: 'XG_FOB_USD' (exports) or 'MG_CIF_USD' (imports)
        - start_period: 'YYYY-MM'
        - end_period: 'YYYY-MM'
        - freq: 'M' (monthly) or 'A' (annual)
        - sleep_sec: delay between requests (optional)

        Returns:
        - pandas DataFrame with columns: reporter, partner, indicator, year, month, value
        """

        # Build the URL

# https://open.data.dataexplorer.ukdataservice.ac.uk/rest/data/IMF.STA,IMTS,1.0.0/
# JPN+BRA+PAK.XG_FOB_USD+MG_CIF_USD..M?startPeriod=2024-01&endPeriod=2024-12&dimensionAtObservation=AllDimensions

        reporters_str = reporters if isinstance(reporters, str) else "+".join(reporters)
        partners_str = partners if isinstance(partners, str) else "+".join(partners)
        indicators_str = indicators if isinstance(indicators, str) else "+".join(indicators)
        base_url = "https://open.data.dataexplorer.ukdataservice.ac.uk/rest/data/IMF.STA,IMTS,1.0.0/"
        code = f"{reporters_str}.{indicators_str}.{partners_str}.{freq}"
        url = f"{base_url}{code}"

        params = {
            "startPeriod": start_period,
            "endPeriod": end_period,
            "dimensionAtObservation": "AllDimensions",
        }

        headers = {
            "Accept": "application/vnd.sdmx.genericdata+xml; version=2.1"
        }

        # Fetch data
        response = requests.get(url, params=params, headers=headers, timeout=30)
        if response.status_code == 404:
            return None

        response.raise_for_status()

        # Parse XML
        root = ET.fromstring(response.content)
        ns = {
            'mes': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
            'gen': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic'
        }

        # Extract observations
        data_list = []
        for obs in root.findall(".//gen:Obs", ns):
            obs_key = obs.find("gen:ObsKey", ns)
            obs_val = obs.find("gen:ObsValue", ns)
            if obs_key is not None and obs_val is not None:
                key_dict = {}
                for obs_key_val in obs_key.findall("gen:Value", ns):
                    id = obs_key_val.get('id')
                    info = obs_key_val.get("value")
                    key_dict[id] = info
                # Time period: 'YYYY-MM' or 'YYYY'
                requuired_keys = ("TIME_PERIOD", "COUNTRY", "COUNTERPART_COUNTRY", "INDICATOR")
                if set(requuired_keys) <= key_dict.keys():
                    period = key_dict["TIME_PERIOD"]
                    date_str = ""
                    if freq.upper() == "M":
                        year, month = period.split("-")
                        # month comes with "M01", "M02", ..., so remove "M"
                        month = month[1:]
                        date_str = str(year) + "-" + str(month) + "-01"
                    elif freq.upper() == "A":
                        year, month = period, None
                        date_str = str(year) + "-01-01"
                    reporter = key_dict["COUNTRY"]
                    partner = key_dict["COUNTERPART_COUNTRY"]
                    indicator = key_dict["INDICATOR"]
                    value = float(obs_val.get("value"))
                    data_list.append({
                        "Date": pd.to_datetime(date_str, format="%Y-%m-%d"),
                        "reporter": reporter,
                        "partner": partner,
                        "indicator": indicator,
                        "value": value
                    })

        # Convert to DataFrame
        df = pd.DataFrame(data_list)

        # Optional: sleep to avoid hammering server
        sleep(sleep_sec)

        return df

    def getTradeData(self, ccies):
        indicators = ["XG_FOB_USD", "MG_CIF_USD"]
        startYYYYMM = "1996-01"
        endYYYYMM = "2025-06"

        countries = []
        for value in ccies.values():
            country = value["DOTS"]
            countries.append(country)

        dfs = []
        for reporter in countries:
            for partner in countries:
                if partner != reporter: # and (reporter in selected_reporters):
                    df = self.fetchDotsDataframe(
                        reporters=reporter,
                        partners=partner,
                        indicators=indicators,
                        start_period=startYYYYMM,
                        end_period=endYYYYMM
                    )
                    if df is not None:
                        print(f"reporter: {reporter}, partner: {partner}, indicator: {indicators}, start_period: {startYYYYMM}, endYYYYMM: {endYYYYMM}")
                        dfs.append(df)
        df_all = pd.concat(dfs)
        df_all.to_csv(self.storeFilenameee, index=False)
        return df_all

# -----------------------------------------------------------------------------------
