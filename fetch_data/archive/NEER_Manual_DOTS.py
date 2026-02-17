import requests
import xml.etree.ElementTree as ET
import pandas as pd
from time import sleep

def fetch_dots_dataframe(reporter, partner, indicator, start_period, end_period, freq="M", sleep_sec=1):
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
    base_url = "https://open.data.dataexplorer.ukdataservice.ac.uk/rest/data/IMF.STA,IMTS,1.0.0/"
    code = f"{reporter}.{indicator}.{partner}.{freq}"
    url = f"{base_url}{code}"
    
    params = {
        "startPeriod": start_period,
        "endPeriod": end_period,
        # "dimensionAtObservation": "AllDimensions"
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
    # pandsmdx is not useful because it is not compatible with python 3.13
    data_list = []
    for obs in root.findall(".//gen:Obs", ns):
        obs_dim = obs.find("gen:ObsDimension", ns)
        obs_val = obs.find("gen:ObsValue", ns)
        if obs_dim is not None and obs_val is not None:
            # Time period: 'YYYY-MM' or 'YYYY'
            period = obs_dim.get("value")
            if freq.upper() == "M":
                year, month = period.split("-")
                # month comes with "M01", "M02", ..., so remove "M"
                month = month[1:]
            else:
                year, month = period, None
            value = float(obs_val.get("value"))
            data_list.append({
                "reporter": reporter,
                "partner": partner,
                "indicator": indicator,
                "year": int(year),
                "month": int(month) if month else None,
                "value": value
            })
    
    # Convert to DataFrame
    df = pd.DataFrame(data_list)
    
    # Optional: sleep to avoid hammering server
    sleep(sleep_sec)
    
    return df

def computeManualNEER(ccy, coutry_key, trade_data):
    return None

def get_weight(ccies):
    # indicators = ["TXG_FOB_USD", "TMG_CIF_USD"]
    indicators = ["XG_FOB_USD", "MG_CIF_USD"]
    # startYYYYMM = "1997-01"
    # endYYYYMM = "2025-06"
    startYYYYMM = "1996-01"
    endYYYYMM = "1996-12"

    countries = []
    for value in ccies.values():
        country = value["IMF_DOTS"]
        countries.append(country)

    dfs = []
#     selected_reporters = [
# "PER",
# "PHL",
# "POL",
# "ROU",
# "RUS",
# "SAU",
# "SGP",
# "ZAF",
# "SWE",
# "CHE",
# "THA",
# "TUR",
# "ARE",
# "GBR",
# "USA",
# "VEN",
# "VNM",
# ]
    for reporter in countries:
        for partner in countries:
            if partner != reporter: # and (reporter in selected_reporters):
                for indicator in indicators:
                    df = fetch_dots_dataframe(
                        reporter=reporter,
                        partner=partner,
                        indicator=indicator,
                        start_period=startYYYYMM,
                        end_period=endYYYYMM
                    )
                    if df is not None:
                        print(f"reporter: {reporter}, partner: {partner}, indicator: {indicator}, start_period: {startYYYYMM}, endYYYYMM: {endYYYYMM}")
                        dfs.append(df)
    df_all = pd.concat(dfs)
    return df_all

# print(df.head())
