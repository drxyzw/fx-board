from dotenv import load_dotenv
import os
import pandas as pd
from utils.config import *
from fetch_data.archive.NEER_Manual import computeManualNEER, getTradeData
from fetch_data.PrecomputedNeer import *
from fetch_data.TradeData import *
from fetch_data.FXRateData import *
from fetch_data.NeerWeight import *

load_dotenv()

# country list of IMF

# country list of FRED
# https://fred.stlouisfed.org/release/tables?rid=319&eid=206365#snid=206401
# country list of DOTS
# https://dataexplorer.ukdataservice.ac.uk/vis?lc=en&fs[0]=InternationalMonetaryFund%2C0%7CDirectionofTradeStatistics%23IMF_DTS%23&fs[1]=International%20Monetary%20Fund%2C0%7CInternational%20Trade%20in%20Goods%20%28formerly%20Direction%20of%20Trade%20Statistics%29%23IMF_DTS%23&pg=0&fc=International%20Monetary%20Fund&snb=1&df[ds]=ds-open-data&df[id]=IMTS&df[ag]=IMF.STA&df[vs]=1.0.0&dq=...&pd=2015%2C2021&to[TIME_PERIOD]=false&isAvailabilityDisabled=false
# country list of UN Comtrade
# https://comtradeapi.un.org/files/v1/app/wiki/ComtradePlus_DataItems.xlsx

# Precomputed NEER
# precomputedNeerObj = PrecomputeNeerBis()
precomputedNeerObj = PrecomputeNeerImf()
precomputedNeerDf = precomputedNeerObj.getNeerSeries(ccies, loadFileIfExists=True)
print("finished loading precomputed NEERs")

onlyPrecomputed = precomputedNeerObj.onlyPrecomputed()
if not onlyPrecomputed:
    # Trade data
    tradeData = ImfDotsTradeData()
    tradeDataDf = tradeData.getTradeData(ccies, loadFileIfExists=True)
    print("finished loading trade data")

    # Weight from trade data
    neerWeight = ImfNeerWeight(tradeData=tradeDataDf)
    neerWeight.computeWeight()


    # Bilateral FX
    fxRateData = BisFXRateData()
    fxRateDataDf = fxRateData.getFxSeries(ccies, loadFileIfExists=True)

    
# onlyPrecomputed = all([not(value["FRED"] is None) for value in ccies.values() ])  
# df_dots_weight = None
# if not onlyPrecomputed:
#     DOTS_TRADE_DATA = "./data_raw/dots_trade_data.csv"
#     if os.path.isfile(DOTS_TRADE_DATA):
#         df_dots_trade_data = pd.read_csv(DOTS_TRADE_DATA)
#     else:
#         df_dots_trade_data = get_weight(ccies)
#         df_dots_trade_data.to_csv(DOTS_TRADE_DATA, index=False)

# NEER_df = None

# NEER_dfs = []
# fred = Fred(api_key=api_key)
# for ccy, value in ccies.items():
#     fred_key = value["FRED"]
#     isInclude = value["Include"]
#     if isInclude:
#         if fred_key is not None:
#             NEER_country = fred.get_series("NB" + fred_key + "BIS").to_frame()
#         else:
#             dots_key = value["IMF_DOTS"]
#             NEER_country = computeManualNEER(ccy, dots_key, df_dots_trade_data)
#         print(f'fetched currency {ccy} from web')
#         NEER_country.columns = [ccy]
#         NEER_dfs.append(NEER_country)

# NEER_df = pd.concat(NEER_dfs, axis=1)

# print('fetched all currncies from web')

# NEER_df.to_excel(DIR_RAW + "/FRED_NEER.xlsx", index=True)
# print('saved in a file')
