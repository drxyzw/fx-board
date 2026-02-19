from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
from utils.utils import *
from utils.config import *

class NeerCalculator:
    storeFilename = ""
    freq = ""
    neerWeightDf = None
    neerWeightDfInterp = None
    fxRateDataDf = None
    def __init__(self, neerWeightDf, fxRateDataDf):
        load_dotenv()
        self.freq = os.getenv("FX_RATE_FREQ")
        freq_label = freqToString(self.freq)
        self.storeFilename = os.getenv("NEER_STORE_DIR") + f"/NEER_{freq_label.upper()}.csv"
        self.neerWeightDf = neerWeightDf
        self.fxRateDataDf = fxRateDataDf
        # for convenience, replace countries with their currencies
        country2Ccy = {v["IMF_DOTS"]: k for k, v in ccies.items()}
        self.neerWeightDf["reporter"] = self.neerWeightDf["reporter"].map(country2Ccy).fillna(self.neerWeightDf["reporter"])
        self.neerWeightDf["partner"] = self.neerWeightDf["partner"].map(country2Ccy).fillna(self.neerWeightDf["partner"])
        weightLag = parseTimeDelta(os.getenv("WEIGHT_LAG"))
        self.neerWeightDf.index=pd.to_datetime(self.neerWeightDf.index).map(lambda x: x + weightLag)

        # further, interpolate weight
        dates = list(self.fxRateDataDf.index)
        dates_num = [date.timestamp() for date in dates]
        neerWeightDfTimestamp = neerWeightDf.copy()
        neerWeightDfTimestamp.index = [t.timestamp() for t in neerWeightDf.index]
        neerWeightDfInterps = []
        for reporter in neerWeightDfTimestamp["reporter"].unique():
            for partner in neerWeightDfTimestamp["partner"].unique():
                originalNeerWeightDf = neerWeightDfTimestamp[(neerWeightDfTimestamp["reporter"] == reporter)
                                                            & (neerWeightDfTimestamp["partner"] == partner)]
                if not originalNeerWeightDf.empty:
                    ts = originalNeerWeightDf.index
                    ws = originalNeerWeightDf["weight"]
                    # for i, date_num in enumerate(dates_num):
                    #     neerWeightDfInterpDict = {}
                    #     neerWeightDfInterpDict["Date"] = dates[i]
                    #     neerWeightDfInterpDict["reporter"] = reporter
                    #     neerWeightDfInterpDict["partner"] = partner
                    #     weight = np.interp(date_num, ts, ws)
                    #     neerWeightDfInterpDict["weight"] = weight
                    #     neerWeightDfInterps.append(neerWeightDfInterpDict)

                    # vectorize
                    weights = np.interp(dates_num, ts, ws)
                    # neerWeightDfInterpDict = {
                    #     "Date": dates,
                    #     "reporter": reporter,
                    #     "partner": partner,
                    #     "weight": weights,
                    # }
                    # neerWeightDfInterps.append(neerWeightDfInterpDict)
                    neerWeightDfInterpPerCcyPair = pd.DataFrame(columns=["Date", "reporter", "partner", "weight"])
                    neerWeightDfInterpPerCcyPair["Date"] = dates
                    neerWeightDfInterpPerCcyPair["reporter"] = reporter
                    neerWeightDfInterpPerCcyPair["partner"] = partner
                    neerWeightDfInterpPerCcyPair["weight"] = weights
                    neerWeightDfInterps.append(neerWeightDfInterpPerCcyPair)
        # neerWeightDfInterp = pd.DataFrame(neerWeightDfInterps)
        neerWeightDfInterp = pd.concat(neerWeightDfInterps)
        neerWeightDfInterp = neerWeightDfInterp.set_index("Date")
        self.neerWeightDfInterp = neerWeightDfInterp
        print("initialized NEER weight")

        # Normalize FX rate by base year
        base_year = int(os.getenv("NEER_BASE_YEAR"))
        base_year_mask = [t.year == base_year for t in self.fxRateDataDf.index]
        base_year_fx_rate = self.fxRateDataDf[base_year_mask].mean()
        self.fxRateDataDf = self.fxRateDataDf / base_year_fx_rate
        print("initialized NEER fx rate")

    def calculate(self):
        # NEER for a country i at a time t
        # ln(NEER_it) = \sum_j w_ijt ln(c_jt / c_it)
        # - c_it: value of USD1 in the unit curency i at t
        # ln(NEER_it) = \sum_j w_ijt [ln(c_jt) - ln(c_it)]
        #             = \sum_j w_ijt ln(c_jt) - \sum_j w_ijt ln(c_it)
        #             = wln - ln(c_it)
        # wln         = [\sum_j w_ijt ln(c_jt)] - ln(c_it)


        ccies_list = list(self.fxRateDataDf.columns)
        dates = list(self.fxRateDataDf.index)
        NEER_dfs = []
        neerWeightDfInterpPivot = pd.pivot_table(self.neerWeightDfInterp, values="weight", index=["Date", "reporter"], columns="partner")
        neerWeightDfInterpPivot = neerWeightDfInterpPivot[list(self.fxRateDataDf.columns)]
        neerWeightDfInterpPivot = neerWeightDfInterpPivot.reset_index().set_index("Date")
        neerWeightDfInterpPivot.columns.name = None
        lnFx = np.log(self.fxRateDataDf)
        for report_ccy in ccies_list:
            # vectorize
            weights_report_ccy = neerWeightDfInterpPivot[(neerWeightDfInterpPivot["reporter"] == report_ccy)]
            weight_report_ccy_ordered = weights_report_ccy[self.fxRateDataDf.columns]
            wln = (weight_report_ccy_ordered * lnFx).sum(axis=1, skipna=True)
            ln_NEER_df_ccy = (wln - lnFx[report_ccy]).to_frame()
            NEER_df_ccy = np.exp(ln_NEER_df_ccy) * 100
            NEER_df_ccy.columns = [report_ccy]
            NEER_dfs.append(NEER_df_ccy)
        #     for date in dates:
        #         weights_ccy_date = self.neerWeightDfInterp[(self.neerWeightDfInterp["reporter"] == report_ccy)
        #                                                      & (self.neerWeightDfInterp.index == date)]
        #         partner_ccies = weights_ccy_date["partner"]
        #         if not partner_ccies.empty:
        #             weights = weights_ccy_date["weight"]
        #             fx_rate_t = self.fxRateDataDf[self.fxRateDataDf.index == date]
        #             fx_rate_t_partner = fx_rate_t[partner_ccies]
        #             wln = np.dot(weights, np.nan_to_num(np.log((fx_rate_t_partner.T))))
        #             ln_neer = wln - np.log(fx_rate_t[report_ccy])
        #             neer = np.exp(ln_neer) * 100
        #             NEER_dfs.append(pd.DataFrame({
        #                 "Date": date,
        #                 "reporter": report_ccy,
        #                 "neer": neer
        #             }))
        # NEER_df = pd.concat(NEER_dfs)
        # NEER_df = pd.pivot_table(NEER_df, values="neer", index="reporter", columns="Date")

        NEER_df = pd.concat(NEER_dfs, axis=1)
        NEER_df.to_csv(self.storeFilename, index=True)
        return NEER_df

