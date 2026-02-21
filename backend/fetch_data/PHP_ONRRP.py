import requests
import os
import pandas as pd
import numpy as np
from utils.config import *

excel_url = "https://www.bsp.gov.ph/Statistics/Financial%20System%20Accounts/sdir.xls"

FETCH_ONLINE_DATA = True # False if using the existing data, True if newly downloading the data

FILENAME = "sdir.xls"
os.makedirs(DIR_RAW, exist_ok=True)
file_path = os.path.join(DIR_RAW, FILENAME)

# newly download data
if FETCH_ONLINE_DATA:
    try:
        res = requests.get(excel_url, stream=True)
        res.raise_for_status()
        with open(file_path, "wb") as f:
            for chunk in res.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded {FILENAME} to {DIR_RAW}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# load the file
df = pd.read_excel(file_path, sheet_name="MONTHLY", skiprows=4, header=[0, 1])
# cleaning
df = df.replace(["…", "-", "..", "...", ' .', "p", "p,r"], np.nan)
df_dropna = df.dropna(axis="columns", how="all")
df_dropna = df_dropna[2:]
# Sorting out month
df_dropna['Year'] = pd.to_numeric(df_dropna[('Date', 'Unnamed: 1_level_1')], errors="coerce")
df_dropna['Year'] = df_dropna['Year'].ffill()
mask = pd.to_numeric(df_dropna[('Date', 'Unnamed: 1_level_1')], errors="coerce").notna()
df_dropna = df_dropna[~mask]
# remove an empty first column
df_dropna = df_dropna[[df_dropna.columns.values[-1]] + list(df_dropna.columns.values[1:-1])]
# remove footnotes rows
dict_month_label = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
df_dropna[('Date', 'Unnamed: 1_level_1')] = df_dropna[('Date', 'Unnamed: 1_level_1')].map(dict_month_label)
df_dropna = df_dropna.dropna(subset=[('Date', 'Unnamed: 1_level_1')])
# flatten columns
new_columns = []
regex_remove = r"[\n\t\r\f\v]"
df = df.replace(regex_remove, "", regex=True)
for i in range(len(df_dropna.columns)):
    col1, col2 = df_dropna.columns.values[i]
    col1
    new_col = col1 if (col2 == '' or col2.startswith("Unnamed:")) else (col1 + "|" + col2)
    new_columns.append(new_col)
df_dropna.columns = new_columns
df_dropna.columns = df_dropna.columns.str.replace(regex_remove, "", regex=True)
# type
df_dropna['Year'] = df_dropna['Year'].astype(int)
df_dropna = df_dropna.rename (columns={"Date": "Month"})
df_dropna['Month'] = df_dropna['Month'].astype(int)
df_dropna.reset_index(drop=True)
# divide by 100 to make it percent
for col in df_dropna.columns[2:]:
    df_dropna[col] = df_dropna[col].astype(float) / 100.
# save
df_dropna.to_excel(DIR_RAW  + "/sdir_formatted.xlsx", index=False)
print("loadeed & formatted & saved all columns")

# extract
df_rrp = df_dropna[["Year", "Month", "Target RRP Rate6|(as of end of period)"]].dropna()
df_rrp.to_excel(DIR_RAW  + "/PHP_ONRRP.xlsx", index=False)
print("saved PHP_ONRRP")



