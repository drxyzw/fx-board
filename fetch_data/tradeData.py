from dotenv import load_dotenv
import os
load_dotenv()

class TradeData:
    storeFilename = ""
    freq = ""
    def __init__(self):
        self.freq = os.getenv("TRADE_FREQ")

    def getTradeData(self, ccies):
        pass

class ImfDotsTradeData(TradeData):
    def __init__(self, freq="M"):
        self.storeFilename = os.getenv("TRADE_DATA_STORE_DIR") + "/imf_dots_trade_data.xlsx"


