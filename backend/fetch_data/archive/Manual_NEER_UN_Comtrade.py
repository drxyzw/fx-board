from dotenv import load_dotenv
import comtradeapicall
import os
import pandas as pd
from utils.config import *

UN_COMTRADE_PRIMARY_API_KEY = load_dotenv("UN_COMTRADE_PRIMARY_API_KEY")

df = comtradeapicall.previewFinalData(
    typeCode="C",       # commodities
    freqCode="A",       # annual
    clCode="HS",        # harmonized system
    # period="2022",      # year
    period="2000",      # year
    reporterCode="842", # country
    # partnerCode="0",    # all partners
    partnerCode=None,    # all partners
    partner2Code=None,
    customsCode=None,
    motCode=None,
    flowCode="X",       # X=export, M=import
    cmdCode="TOTAL",    # total trade
)

if not df.empty:
    trade_per_partner = df[["period", "reporterDesc", "flowDesc", "primaryValue"]]
    print(trade_per_partner.head())
else:
    print("No data found")
    raise ValueError("No data found")