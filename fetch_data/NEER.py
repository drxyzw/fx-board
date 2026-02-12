from dotenv import load_dotenv
from fredapi import Fred
import os
import pandas as pd
from utils.config import *
from fetch_data.NEER_Manual import computeManualNEER, get_weight

load_dotenv()
api_key = os.getenv("FRED_API_KEY")
# print("apikey: "+ api_key)
# country list of IMF

# country list of FRED
# https://fred.stlouisfed.org/release/tables?rid=319&eid=206365#snid=206401
# country list of DOTS
# https://dataexplorer.ukdataservice.ac.uk/vis?lc=en&fs[0]=InternationalMonetaryFund%2C0%7CDirectionofTradeStatistics%23IMF_DTS%23&fs[1]=International%20Monetary%20Fund%2C0%7CInternational%20Trade%20in%20Goods%20%28formerly%20Direction%20of%20Trade%20Statistics%29%23IMF_DTS%23&pg=0&fc=International%20Monetary%20Fund&snb=1&df[ds]=ds-open-data&df[id]=IMTS&df[ag]=IMF.STA&df[vs]=1.0.0&dq=...&pd=2015%2C2021&to[TIME_PERIOD]=false&isAvailabilityDisabled=false
# country list of UN Comtrade
# https://comtradeapi.un.org/files/v1/app/wiki/ComtradePlus_DataItems.xlsx



ccies = {
    "DZD": {"Include": True, "IMF":   None, "FRED": "DZ", "DOTS": "DZA", "UNCT": 12}, # Algerian dinar
    "ARS": {"Include": True, "IMF":   None, "FRED": "AR", "DOTS": "ARG", "UNCT": 32}, # Argentina peso
    "AUD": {"Include": True, "IMF":  "AUS", "FRED": "AU", "DOTS": "AUS", "UNCT": 36},
    "BDT": {"Include": True, "IMF":   None, "FRED": None, "DOTS": "BGD", "UNCT": 50}, # Bangladesh taka
    "BRL": {"Include": True, "IMF":  "BRA", "FRED": "BR", "DOTS": "BRA", "UNCT": 76},
    "KHR": {"Include": True, "IMF":   None, "FRED": None, "DOTS": "KHN", "UNCT": 116}, # Cambodian riel
    "CAD": {"Include": True, "IMF":  "CAN", "FRED": "CA", "DOTS": "CAN", "UNCT": 124},
    "CLP": {"Include": True, "IMF":  "CHL", "FRED": "CL", "DOTS": "CHL", "UNCT": 152}, # Chilean peso
    "CNY": {"Include": True, "IMF":  "CHN", "FRED": "CN", "DOTS": "CHN", "UNCT": 156},
    "NTD": {"Include": True, "IMF":   None, "FRED": "TW", "DOTS": "TWN", "UNCT": 490}, # https://www.cepii.fr/DATA_DOWNLOAD/baci/doc/FAQ_BACI.html#7_Is_there_data_for_Taiwan , https://groups.google.com/g/witsforum/c/gXaRZfScejg
    "COP": {"Include": True, "IMF":  "COL", "FRED": "CO", "DOTS": "COL", "UNCT": 170}, # Colombian peso
    "EUR": {"Include": True, "IMF": "G163", "FRED": "XM", "DOTS": "G995","UNCT": 97},
    "CZK": {"Include": True, "IMF":  "CZE", "FRED": "CZ", "DOTS": "CZE", "UNCT": 203}, # Czech Koruna
    "DKK": {"Include": True, "IMF":  "DNK", "FRED": "DK", "DOTS": "DNK", "UNCT": 208},
    "HKD": {"Include": True, "IMF":  "HKG", "FRED": "HK", "DOTS": "HKG", "UNCT": 344},
    "HUF": {"Include": True, "IMF":  "HUN", "FRED": "HU", "DOTS": "HUN", "UNCT": 348}, # Hungary forint
    "ISK": {"Include": True, "IMF":  "ISL", "FRED": "IS", "DOTS": "ISL", "UNCT": 352}, # Iceland Krona
    "INR": {"Include": True, "IMF":   None, "FRED": "IN", "DOTS": "IND", "UNCT": 699},
    "IDR": {"Include": True, "IMF":   None, "FRED": "ID", "DOTS": "IDN", "UNCT": 360},
    "ILS": {"Include": True, "IMF":  "ISR", "FRED": "IL", "DOTS": "ISR", "UNCT": 376}, # Israeli shekel
    "JPY": {"Include": True, "IMF":  "JPN", "FRED": "JP", "DOTS": "JPN", "UNCT": 392},
    "KRW": {"Include": True, "IMF":   None, "FRED": "KR", "DOTS": "KOR", "UNCT": 410},
    "MYR": {"Include": True, "IMF":  "MYS", "FRED": "MY", "DOTS": "MYS", "UNCT": 458},
    "MXN": {"Include": True, "IMF":  "MEX", "FRED": "MX", "DOTS": "MEX", "UNCT": 484},
    "NZD": {"Include": True, "IMF":  "NZL", "FRED": "NZ", "DOTS": "NZL", "UNCT": 554},
    "NOK": {"Include": True, "IMF":  "NOR", "FRED": "NO", "DOTS": "NOR", "UNCT": 579}, # Nowegian Krone
    "PEN": {"Include": True, "IMF":   None, "FRED": "PE", "DOTS": "PER", "UNCT": 604}, # Peru sol
    "PHP": {"Include": True, "IMF":  "PHL", "FRED": "PH", "DOTS": "PHL", "UNCT": 608},
    "PKR": {"Include": True, "IMF":  "PAK", "FRED": None, "DOTS": "PAK", "UNCT": 586}, # Pakistan rupee
    "PLZ": {"Include": True, "IMF":  "POL", "FRED": "PL", "DOTS": "POL", "UNCT": 616}, # Polish Zloty
    "RON": {"Include": True, "IMF":  "ROU", "FRED": "RO", "DOTS": "ROU", "UNCT": 642}, # Romanian Leu
    "RUB": {"Include": True, "IMF":  "RUS", "FRED": "RU", "DOTS": "RUS", "UNCT": 643},
    "SAR": {"Include": True, "IMF":  "SAU", "FRED": "SA", "DOTS": "SAU", "UNCT": 682}, # Saudi Riyal
    "SGD": {"Include": True, "IMF":  "SGP", "FRED": "SG", "DOTS": "SGP", "UNCT": 702},
    "ZAR": {"Include": True, "IMF":  "ZAF", "FRED": "ZA", "DOTS": "ZAF", "UNCT": 710},
    "SEK": {"Include": True, "IMF":  "SWE", "FRED": "SE", "DOTS": "SWE", "UNCT": 752}, # Sweden Krona
    "CHF": {"Include": True, "IMF":  "CHE", "FRED": "CH", "DOTS": "CHE", "UNCT": 756},
    "THB": {"Include": True, "IMF":   None, "FRED": "TH", "DOTS": "THA", "UNCT": 764},
    "TRY": {"Include": True, "IMF":   None, "FRED": "TR", "DOTS": "TUR", "UNCT": 792},
    "AED": {"Include": True, "IMF":  "ARE", "FRED": "AE", "DOTS": "ARE", "UNCT": 784},
    "GBP": {"Include": True, "IMF":  "GBR", "FRED": "GB", "DOTS": "GBR", "UNCT": 826},
    "USD": {"Include": True, "IMF":  "USA", "FRED": "US", "DOTS": "USA", "UNCT": 840},
    "VEF": {"Include": True, "IMF":   None, "FRED": "VE", "DOTS": "VEN", "UNCT": 862}, # Venezuelan Bolivar
    "VND": {"Include": True, "IMF":   None, "FRED": None, "DOTS": "VNM", "UNCT": 704},
}

onlyPrecomputed = all([not(value["FRED"] is None) for value in ccies.values() ])  
df_dots_weight = None
if not onlyPrecomputed:
    DOTS_TRADE_DATA = "./data_raw/dots_trade_data.csv"
    if os.path.isfile(DOTS_TRADE_DATA):
        df_dots_trade_data = pd.read_csv(DOTS_TRADE_DATA)
    else:
        df_dots_trade_data = get_weight(ccies)
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
