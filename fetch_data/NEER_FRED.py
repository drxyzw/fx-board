from dotenv import load_dotenv
from fredapi import Fred
import os
import pandas as pd
from utils.config import *
from fetch_data.NEER_Manual import computeManualNEER, dots_weight

load_dotenv()
api_key = os.getenv("FRED_API_KEY")
# print("apikey: "+ api_key)
# country list
# https://fred.stlouisfed.org/release/tables?rid=319&eid=206365#snid=206401

ccies = {
    "DZD": {"Include": True, "FRED": "DZ", "DOTS": "DZA"}, # Algerian dinar
    "ARS": {"Include": True, "FRED": "AR", "DOTS": "ARG"}, # Argentina peso
    "AUD": {"Include": True, "FRED": "AU", "DOTS": "AUS"},
    "BRL": {"Include": True, "FRED": "BR", "DOTS": "BRA"},
    "KHR": {"Include": True, "FRED": None, "DOTS": "KHN"}, # Cambodian riel
    "CAD": {"Include": True, "FRED": "CA", "DOTS": "CAN"},
    "CLP": {"Include": True, "FRED": "CL", "DOTS": "CHL"}, # Chilean peso
    "CNY": {"Include": True, "FRED": "CN", "DOTS": "CHN"},
    "NTD": {"Include": True, "FRED": "TW", "DOTS": "TWN"},
    "COP": {"Include": True, "FRED": "CO", "DOTS": "COL"}, # Colombian peso
    "EUR": {"Include": True, "FRED": "XM", "DOTS": "G995"},
    "CZK": {"Include": True, "FRED": "CZ", "DOTS": "CZE"}, # Czech Koruna
    "DKK": {"Include": True, "FRED": "DK", "DOTS": "DNK"},
    "HKD": {"Include": True, "FRED": "HK", "DOTS": "HKG"},
    "HUF": {"Include": True, "FRED": "HU", "DOTS": "HUN"}, # Hungary forint
    "ISK": {"Include": True, "FRED": "IS", "DOTS": "ISL"}, # Iceland Krona
    "INR": {"Include": True, "FRED": "IN", "DOTS": "IND"},
    "IDR": {"Include": True, "FRED": "ID", "DOTS": "IDN"},
    "ILS": {"Include": True, "FRED": "IL", "DOTS": "ISR"}, # Israeli shekel
    "JPY": {"Include": True, "FRED": "JP", "DOTS": "JPN"},
    "KRW": {"Include": True, "FRED": "KR", "DOTS": "KOR"},
    "MYR": {"Include": True, "FRED": "MY", "DOTS": "MYS"},
    "MXN": {"Include": True, "FRED": "MX", "DOTS": "MEX"},
    "NZD": {"Include": True, "FRED": "NZ", "DOTS": "NZL"},
    "NOK": {"Include": True, "FRED": "NO", "DOTS": "NOR"}, # Nowegian Krone
    "PEN": {"Include": True, "FRED": "PE", "DOTS": "PER"}, # Peru sol
    "PHP": {"Include": True, "FRED": "PH", "DOTS": "PHL"},
    "PLZ": {"Include": True, "FRED": "PL", "DOTS": "POL"}, # Polish Zloty
    "RON": {"Include": True, "FRED": "RO", "DOTS": "ROU"}, # Romanian Leu
    "RUB": {"Include": True, "FRED": "RU", "DOTS": "RUS"},
    "SAR": {"Include": True, "FRED": "SA", "DOTS": "SAU"}, # Saudi Riyal
    "SGD": {"Include": True, "FRED": "SG", "DOTS": "SGP"},
    "ZAR": {"Include": True, "FRED": "ZA", "DOTS": "ZAF"},
    "SEK": {"Include": True, "FRED": "SE", "DOTS": "SWE"}, # Sweden Krona
    "CHF": {"Include": True, "FRED": "CH", "DOTS": "CHE"},
    "THB": {"Include": True, "FRED": "TH", "DOTS": "THA"},
    "TRY": {"Include": True, "FRED": "TR", "DOTS": "TUR"},
    "AED": {"Include": True, "FRED": "AE", "DOTS": "ARE"},
    "GBP": {"Include": True, "FRED": "GB", "DOTS": "GBR"},
    "USD": {"Include": True, "FRED": "US", "DOTS": "USA"},
    "VEF": {"Include": True, "FRED": "VE", "DOTS": "VEN"}, # Venezuelan Bolivar
    "VND": {"Include": True, "FRED": None, "DOTS": "VNM"},
}

onlyFred = True
for value in ccies.values():
    isManual_ccy = value["FRED"] is None
    onlyFred = onlyFred and (not isManual_ccy)
df_dots_weight = None
if not onlyFred:
    DOTS_TRADE_DATA = "./data_raw/dots_trade_data.csv"
    if os.path.isfile(DOTS_TRADE_DATA):
        df_dots_trade_data = pd.read_csv(DOTS_TRADE_DATA)
    else:
        df_dots_trade_data = dots_weight(ccies)
        df_dots_trade_data.to_csv(DOTS_TRADE_DATA, index=False)

NEER_dfs = []
fred = Fred(api_key=api_key)
for ccy, value in ccies.items():
    fred_key = value["FRED"]
    isInclude = value["Include"]
    if isInclude:
        if fred_key is not None:
            NEER_country = fred.get_series("NB" + fred_key + "BIS").to_frame()
        else:
            dots_key = value["DOTS"]
            NEER_country = computeManualNEER(ccy, dots_key, df_dots_trade_data)
        print(f'fetched currency {ccy} from web')
        NEER_country.columns = [ccy]
        NEER_dfs.append(NEER_country)

NEER_df = pd.concat(NEER_dfs, axis=1)

print('fetched all currncies from web')

NEER_df.to_excel(DIR_RAW + "/FRED_NEER.xlsx", index=True)
print('saved in a file')
