import sdmx

IMF_DATA = sdmx.Client('IMF_DATA')
ccies = {"USD": "USA",
         "AED": "ARE",
         "EUR": "G163",
         "CAD": "CAN",
         "CHF": "CHE",
         "GBP": "GBR",
         "ILS": "ISR",
         "AUD": "AUS",
         "NZD": "NZL",
         "JPY": "JPN",
         "PHP": "PHL",
#         "KRW", "TWD",
         "CNY": "CHN", "HKD": "HKG",
         "SGD": "SGP",
         "MYR": "MYS",
#         "THB", "VND", "INR",
         "RUB": "RUS",
         "BRL": "BRA",
         "ZAR": "ZAF"
         }
res_NEER = "EER"
key_NEER = "JPN.NEER_IX_RY2010_ACW.M"
startYear = 2010
# startYear = 2000
data_msg = IMF_DATA.data(res_NEER, key=key_NEER, params={"startPeriod": startYear})

df = sdmx.to_pandas(data_msg)
print(df.head(13))
