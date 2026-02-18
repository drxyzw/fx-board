from dotenv import load_dotenv
import os
from utils.utils import *

class NeerCalculator:
    storeFilename = ""
    freq = ""
    neerWeightDf = None
    fxRateDataDf = None
    def __init__(self, neerWeightDf, fxRateDataDf):
        load_dotenv()
        self.freq = os.getenv("FX_RATE_FREQ")
        freq_label = freqToString(self.freq)
        self.storeFilename = os.getenv("NEER_STORE_DIR") + f"NEER_{freq_label.upper}.csv"
        self.neerWeightDf = neerWeightDf
        self.fxRateDataDf = fxRateDataDf
    def calculate(self):
        pass
    