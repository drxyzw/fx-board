from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from dateutil import relativedelta as dt

from utils.utils import *
from utils.config import *

class NeerCalculator:
    storeFilename = ""
    storeDetailFilename = ""
    freq = ""
    neerWeightDf = None
    neerWeightDfInterp = None
    fxRateDataDf = None
    def __init__(self, neerWeightDf, fxRateDataDf):
        load_dotenv()
        self.freq = os.getenv("FX_RATE_FREQ")
        freq_label = freqToString(self.freq)
        self.storeFilename = os.getenv("NEER_STORE_DIR") + f"/NEER_{freq_label.upper()}.csv"
        self.storeDetailFilename = os.getenv("NEER_STORE_DIR") + f"/NEER_DETAIL_{freq_label.upper()}.parquet"
        self.neerWeightDf = neerWeightDf
        self.fxRateDataDf = fxRateDataDf
        # for convenience, replace countries with their currencies
        country2Ccy = {v["IMF_DOTS"]: k for k, v in ccies.items()}
        self.neerWeightDf["reporter"] = self.neerWeightDf["reporter"].map(country2Ccy).fillna(self.neerWeightDf["reporter"])
        self.neerWeightDf["partner"] = self.neerWeightDf["partner"].map(country2Ccy).fillna(self.neerWeightDf["partner"])
        weightLag = parseTimeDelta(os.getenv("WEIGHT_LAG"))
        # use weight up to previous year due to time lag of trade data update
        self.neerWeightDf.index=pd.to_datetime(self.neerWeightDf.index).map(lambda x: x + weightLag)
        # replace NaN weight with 0
        # self.neerWeightDf = self.neerWeightDf.fillna(0.0)
        # flat extrapolation to 1Y
        lastDate = self.neerWeightDf.index[-1]
        dfLastDate = self.neerWeightDf.loc[lastDate].copy()
        lastDate += dt(years=1)
        dfLastDate.index = [lastDate] * len(dfLastDate)
        self.neerWeightDf = pd.concat([self.neerWeightDf, dfLastDate])

        # further, interpolate weight
        dates = list(self.fxRateDataDf.index)
        dates_num = [date.timestamp() for date in dates]
        neerWeightDfTimestamp = self.neerWeightDf.copy()
        neerWeightDfTimestamp.index = [t.timestamp() for t in neerWeightDfTimestamp.index]
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
                    # weights = np.interp(dates_num, ts, ws)
                    # interpolator = interp1d(ts, ws, bounds_error=False, fill_value=np.nan)
                    interpolator = interp1d(ts, ws, bounds_error=False, fill_value=0.0)
                    weights = interpolator(dates_num)
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
        #             = \sum_j w_ijt wln_ij
        # where wln   = ln(c_jt) - ln(c_it)
        # or,
        #             = \sum_j w_ijt ln(c_jt) - \sum_j w_ijt ln(c_it)
        #             = wln - ln(c_it)
        # wln_partner = [\sum_j w_ijt ln(c_jt)] - ln(c_it)

        ccies_list = list(self.fxRateDataDf.columns)
        NEER_dfs = []
        NEER_detial_dfs = []
        neerWeightDfInterpPivot = pd.pivot_table(self.neerWeightDfInterp, values="weight", index=["Date", "reporter"], columns="partner")
        neerWeightDfInterpPivot = neerWeightDfInterpPivot[list(self.fxRateDataDf.columns)]
        neerWeightDfInterpPivot = neerWeightDfInterpPivot.reset_index().set_index("Date")
        neerWeightDfInterpPivot.columns.name = None
        lnFx = np.log(self.fxRateDataDf)
        for report_ccy in ccies_list:
            # vectorize
            weights_report_ccy = neerWeightDfInterpPivot[(neerWeightDfInterpPivot["reporter"] == report_ccy)]
            weight_report_ccy_ordered = weights_report_ccy[self.fxRateDataDf.columns]
            # wln_partner = (weight_report_ccy_ordered * lnFx).sum(axis=1, skipna=True)
            # ln_NEER_df_ccy = (wln_partner - lnFx[report_ccy]).to_frame()
            lnFxMinuslnReportCcy = lnFx.subtract(lnFx[report_ccy], axis=0)
            # forward-fill to all FX rates are non-nan. So no discontinuity in weighted average FX pair
            lnFxMinuslnReportCcy = lnFxMinuslnReportCcy.ffill()
            contribution = (weight_report_ccy_ordered * lnFxMinuslnReportCcy)
            wln = contribution.sum(axis=1, skipna=True, min_count=1).ffill()
            ln_NEER_df_ccy = wln.to_frame()
            NEER_df_ccy = np.exp(ln_NEER_df_ccy) * 100
            # first few rows are 0, NaN, or 100., and we replace it with NaN
            NEER_df_ccy.columns = [report_ccy]
            is_valid = ~NEER_df_ccy[report_ccy].isin([0.0, np.nan, 100])
            has_started = is_valid.cummax()
            NEER_df_ccy.loc[~has_started, report_ccy] = np.nan
            # save detail file
            # columns: Date, reporter, partner, weight, return, contribution
            for partner_ccy in self.fxRateDataDf.columns:
                weight_report_partner_ccy_ordered = weight_report_ccy_ordered[partner_ccy].dropna().to_frame().rename(columns={partner_ccy: "weight"})
                if not weight_report_partner_ccy_ordered.empty:
                    weight_report_partner_ccy_ordered["return"] = lnFxMinuslnReportCcy[partner_ccy]
                    weight_report_partner_ccy_ordered["contribution"] = contribution[partner_ccy]
                    weight_report_partner_ccy_ordered["reporter"] = report_ccy
                    weight_report_partner_ccy_ordered["partner"] = partner_ccy
                    weight_report_partner_ccy_ordered = weight_report_partner_ccy_ordered[["reporter", "partner", "weight", "return", "contribution"]]
                    NEER_detial_dfs.append(weight_report_partner_ccy_ordered)
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

        # remove 0 or na in "contribution"
        NEER_detail_df = pd.concat(NEER_detial_dfs).dropna(subset="weight")
        NEER_detail_df = NEER_detail_df[NEER_detail_df["weight"] > 1.0e-4]
        NEER_detail_df.to_parquet(self.storeDetailFilename, index=True)
        NEER_detail_df.to_csv(self.storeDetailFilename.replace("parquet", "csv"), index=True)
        return NEER_df

