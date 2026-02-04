# import sdmx
# import pandas as pd

# client = sdmx.Client("IMF")
# res = client.data(
#     resource_id="DOT",
#     key={
#         "FREQ": "M",
#         "REF_AREA": "VNM",
#         "COUNTERPART_AREA": ["USA", "CHN", "JPN", "KOR", "DEU"],
#         "INDICATOR": ["TXG_FOB_USD", "TMG_CIF_USD"],
#     },
#     params={
#         "startPeriod": "2000-01",
#         "endPeriod": "2000-02",
#     },
#     validate=False, # to bypass an errneous dataFlow/latest
# )

# df = res.to_pandas()
# print(type(df))
# print(df.head())


# import requests
# import pandas as pd

# url = (
#     "https://dataservices.imf.org/REST/SDMX_JSON.svc/"
#     "CompactData/DOT/M.VNM.USA.TXG_FOB_USD"
#     "?startPeriod=2000-01&endPeriod=2000-02"
# )

# r = requests.get(url)
# data = r.json()

# import requests
# url = 'http://dataservices.imf.org/REST/SDMX_JSON.svc/'
# key = 'CompactData/IFS/M.GB.PMP_IX' # adjust codes here

# # Navigate to series in API-returned JSON data
# data = (requests.get(f'{url}{key}').json()
#         ['CompactData']['DataSet']['Series'])

# print(data['Obs'][-1]) # Print latest observation



# import requests

# # url = "https://dataservices.imf.org/REST/SDMX_JSON.svc/Dataflow"
# url = (
#     "https://sdmxcentral.imf.org/REST/SDMX_JSON.svc/Data/"
#     "IMTS/M.JPN.X..USD?"
#     "startPeriod=2020-01&endPeriod=2024-12"
# )
# r = requests.get(url, timeout=60)
# r.raise_for_status()
# resp = r.json()

# # Find IMTS dataset
# flows = resp["Structure"]["Dataflows"]["Dataflow"]
# imts = [f for f in flows if "IMTS" in f["KeyFamilyRef"]["KeyFamilyID"]]

# print(imts)



# import requests
# from requests.adapters import HTTPAdapter
# from urllib3.util.retry import Retry

# session = requests.Session()

# retries = Retry(
#     total=5,
#     backoff_factor=1.5,
#     status_forcelist=[429, 500, 502, 503, 504],
#     allowed_methods=["GET"]
# )

# adapter = HTTPAdapter(max_retries=retries)
# session.mount("https://", adapter)

# url = "https://sdmxcentral.imf.org/REST/SDMX_JSON.svc/Dataflow"

# r = session.get(url, timeout=30)
# r.raise_for_status()
# data = r.json()

# import requests
# import pandas as pd

# BASE = "https://sdmxcentral.imf.org/REST/SDMX_JSON.svc"

# # Example: Japan exports to world, monthly
# url = (
#     f"{BASE}/Data/IMTS/"
#     "JPN.XG_FOB_USD.G001.M"
#     "?startPeriod=2020-01&endPeriod=2024-12"
# )

# r = requests.get(url, timeout=30)
# r.raise_for_status()
# data = r.json()

# # Parse the observations
# series = data["CompactData"]["DataSet"]["Series"]
# obs = series["Obs"]

# df = pd.DataFrame(obs)
# df["@TIME_PERIOD"] = pd.to_datetime(df["@TIME_PERIOD"])
# df["@OBS_VALUE"] = pd.to_numeric(df["@OBS_VALUE"])

# df = df.rename(columns={
#     "@TIME_PERIOD": "date",
#     "@OBS_VALUE": "value"
# })

# print(df.head())


# import requests

# url = "https://sdmxcentral.imf.org/ws/public/sdmxapi/rest/Dataflow"
# headers = {
#     "Accept": "application/vnd.sdmx.structures+json;version=2.1"
# }

# r = requests.get(url, headers=headers, timeout=30)
# r.raise_for_status()
# data = r.json()

# for df in data.get("dataflows", []):
#     print(df["id"], "-", df.get("name", {}).get("en", ""))

# from pandasdmx import Request
# imf = Request('IMF')  # pandasdmx knows IMF endpoints
# flows = imf.dataflow()  # lists all available datasets
# print(flows.dataflow.keys())  # shows IMTS, IFS, etc.

# import pandas as pd
# import sdmx
# import json
# IMF_DATA = sdmx.Client("IMF_DATA")
# # dsd = IMF_DATA.datastructure('IMTS')
# f = IMF_DATA.dataflow('IMTS')
# dsd_id = list(f.structure.keys())[0] # 'DSD_IMTS'
# dsd = IMF_DATA.datastructure(dsd_id)
# # export IMTS keywords
# isExportIMTSkey = False
# if isExportIMTSkey:
#     with open("./IMTS_PARAMETER.txt", "w", encoding="utf-8") as file:
#         for cl in dsd.codelist:
#             file.write(f"Codelist ID: {cl}")
#             file.write("\n")
#             for id, code in dsd.codelist[cl].items.items():
#                 file.write(f"{id}, {code.name}")
#                 file.write("\n")

# # # export DOT keywords
# IMF = sdmx.Client("IMF")
# flows = IMF.dataflow().dataflow
# print("DOTS" in flows)
# isExportDOTSkey = False
# if isExportDOTSkey:
#     flow_keys = flows.keys()
#     with open("./DOTS_PARAMETER.txt", "w", encoding="utf-8") as file:
#         for k in flow_keys:
#             if "DOTS" in k:
#                 file.write(k)
#                 file.write("\n")
# # dsd = IMF.datastructure("DOTS")
# # print(dsd)

# key = [
#     ("FREQ", "M"),
#     ("REF_AREA", "JPN"),
#     ("COUNTERPART_AREA", "WLD"),
#     ("INDICATOR", "TXG_FOB_USD"),
#     ("DATA_DOMAIN", "TOT"),
# ]

# data = IMF.data(
#     "DOTS",
#     # key=key,
#     key="M.JPN.WLD.TXG_FOB_USD.TOT",
#     params={
#         "startPeriod": "2020-01",
#         "endPeriod": "2024-12",
#     },
# )

# df = sdmx.to_pandas(data)
# print(df.head())

# import requests
# import pandas as pd

# url = (
#     "https://dataservices.imf.org/REST/SDMX_JSON.svc/"
#     "Data/DOTS/M.JPN.WLD.TXG_FOB_USD.TOT"
# )

# params = {
#     "startPeriod": "2020-01",
#     "endPeriod": "2024-12",
# }

# r = requests.get(url, params=params, timeout=30)
# r.raise_for_status()
# data = r.json()

import requests
import pandas as pd
from itertools import product
from time import sleep
import sdmx


# # ------------------------
# # Configuration
# # ------------------------
# BASE_URL = "https://open.data.dataexplorer.ukdataservice.ac.uk/rest/data/IMF.STA,IMTS,1.0.0/"

# # Reporter countries
# reporters = ["JPN"] #, "USA", "CHN"]  # add more ISO3 country codes as needed

# # Partner countries
# partners = ["USA"] #, "G995", "BRA"]  # use ISO3 codes, e.g., WLD=world, BRA=Brazil

# # Indicators / trade flows
# indicators = ["XG_FOB_USD", "MG_CIF_USD"]  # exports/imports

# # Frequency
# freq = "M"

# # Time range
# start_period = "2020-01"
# end_period = "2025-06"

# # Optional: sleep between requests to be polite to server
# SLEEP_SECONDS = 1

# # ------------------------
# # Helper function to fetch data
# # ------------------------
# def fetch_dots(reporter, partner, indicator):
#     code = f"{reporter}.{indicator}.{partner}.{freq}"
#     url = f"{BASE_URL}{code}"
#     # headers = {
#     #     "Accept": "application/vnd.sdmx.structure+json;version=1.0.0"
#     # }
#     params = {
#         "startPeriod": start_period,
#         "endPeriod": end_period,
#         "dimensionAtObservation": "AllDimensions"
#     }
#     print(f"Fetching {reporter} → {partner} ({indicator})...")
#     response = requests.get(url, params=params, timeout=30)
#     response.raise_for_status()
#     return response.json()  # or response.text if XML

# # ------------------------
# # Loop over all combinations
# # ------------------------
# all_data = []

# for reporter, partner, indicator in product(reporters, partners, indicators):
#     try:
#         data = fetch_dots(reporter, partner, indicator)
#         # Example: append as dict with metadata
#         all_data.append({
#             "reporter": reporter,
#             "partner": partner,
#             "indicator": indicator,
#             "data": data
#         })
#         sleep(SLEEP_SECONDS)
#     except requests.HTTPError as e:
#         print(f"Failed to fetch {reporter} → {partner} ({indicator}): {e}")

# # ------------------------
# # Convert to DataFrame if needed
# # ------------------------
# # You can parse `data` further depending on JSON structure
# # Example: just show first observation for testing
# for entry in all_data:
#     print(entry["reporter"], entry["partner"], entry["indicator"], entry["data"])


