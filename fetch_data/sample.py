import sdmx

IMF_DATA = sdmx.Client('IMF_DATA')
key_JPY_NEER = "JPN.NEER_IX_RY2010_ACW.M"
res_JPY_NEER = "EER"
key_USD_CPI = "USA+CAN.CPI.CP01.IX.M"
res_USD_CPI = 'CPI'
data_msg = IMF_DATA.data(res_JPY_NEER, key=key_JPY_NEER, params={"startPeriod": 2018})

cpi_df = sdmx.to_pandas(data_msg)
print(cpi_df.head())
