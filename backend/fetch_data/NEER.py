from dotenv import load_dotenv
from utils.config import *
from fetch_data.archive.NEER_Manual import computeManualNEER, getTradeData
from fetch_data.PrecomputedNeer import *
from fetch_data.TradeData import *
from fetch_data.FXRateData import *
from fetch_data.NeerWeight import *
from fetch_data.NeerCalculator import *

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

neerWeightDf = None
fxRateDataDf = None
onlyPrecomputed = precomputedNeerObj.onlyPrecomputed()
if not onlyPrecomputed:
    # Trade data
    tradeData = ImfDotsTradeData()
    tradeDataDf = tradeData.getTradeData(ccies, loadFileIfExists=True)
    print("finished loading trade data")

    # Weight from trade data
    neerWeight = ImfNeerWeight(tradeData=tradeDataDf)
    neerWeightDf = neerWeight.computeWeight(loadFileIfExists=False)

    # Bilateral FX
    fxRateData = BisFXRateData()
    fxRateDataDf = fxRateData.getFxSeries(ccies, loadFileIfExists=True)

neerCalculator = NeerCalculator(neerWeightDf=neerWeightDf, fxRateDataDf=fxRateDataDf)
neerDf = neerCalculator.calculate()
    
