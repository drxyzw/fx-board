
import os
from selenium import webdriver
import tempfile

DIR_RAW = "./data_raw"

def isRunOnGitHubActions():
    return isinstance(os.environ.get("GITHUB_ACTIONS"), str) and os.environ.get("GITHUB_ACTIONS").upper() == "TRUE"
    
def makeSeleniumOption():
    selenium_options = webdriver.ChromeOptions()
    selenium_options.add_argument("--no-sandbox")
    selenium_options.add_argument("--disable-dev-shm-usage")
    if isRunOnGitHubActions():
        selenium_options.add_argument("--disable-gpu")
        selenium_options.add_argument("--disable-extensions")
        selenium_options.add_argument("--disable-infobars")
        selenium_options.add_argument("--start-maximized")
        selenium_options.add_argument("--window-size=1920,1080")
        selenium_options.add_argument("--disable-features=VizDisplayCompositor")
        selenium_options.add_argument("--remote-debugging-port=9222")
        selenium_options.add_argument("--user-data-dir=" + tempfile.mkdtemp())
        selenium_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        selenium_options.add_experimental_option("useAutomationExtension", False)
        selenium_options.add_experimental_option("detach", False)

    return selenium_options

ccies = {
    "DZD": {"Include": True, "IMF_NEER":   None, "BIS_NEER": "DZ", "IMF_DOTS": "DZA", "UNCT":  12, "BIS_FX": "DZ", "BIS_FX_DOM": "DZD"}, # Algerian dinar
    "ARS": {"Include": True, "IMF_NEER":   None, "BIS_NEER": "AR", "IMF_DOTS": "ARG", "UNCT":  32, "BIS_FX": "AR", "BIS_FX_DOM": "ARS"}, # Argentina peso
    "AUD": {"Include": True, "IMF_NEER":  "AUS", "BIS_NEER": "AU", "IMF_DOTS": "AUS", "UNCT":  36, "BIS_FX": "AU", "BIS_FX_DOM": "AUD"},
    "BDT": {"Include": True, "IMF_NEER":   None, "BIS_NEER": None, "IMF_DOTS": "BGD", "UNCT":  50, "BIS_FX": None, "BIS_FX_DOM":  None}, # Bangladesh taka
    "BRL": {"Include": True, "IMF_NEER":  "BRA", "BIS_NEER": "BR", "IMF_DOTS": "BRA", "UNCT":  76, "BIS_FX": "BR", "BIS_FX_DOM": "BRL"},
    "KHR": {"Include": True, "IMF_NEER":   None, "BIS_NEER": None, "IMF_DOTS": "KHM", "UNCT": 116, "BIS_FX": None, "BIS_FX_DOM":  None}, # Cambodian riel
    "CAD": {"Include": True, "IMF_NEER":  "CAN", "BIS_NEER": "CA", "IMF_DOTS": "CAN", "UNCT": 124, "BIS_FX": "CA", "BIS_FX_DOM": "CAD"},
    "CLP": {"Include": True, "IMF_NEER":  "CHL", "BIS_NEER": "CL", "IMF_DOTS": "CHL", "UNCT": 152, "BIS_FX": "CL", "BIS_FX_DOM": "CLP"}, # Chilean peso
    "CNY": {"Include": True, "IMF_NEER":  "CHN", "BIS_NEER": "CN", "IMF_DOTS": "CHN", "UNCT": 156, "BIS_FX": "CN", "BIS_FX_DOM": "CNY"},
    "TWD": {"Include": True, "IMF_NEER":   None, "BIS_NEER": "TW", "IMF_DOTS": "TWN", "UNCT": 490, "BIS_FX": "TW", "BIS_FX_DOM": "TWD"}, # https://www.cepii.fr/DATA_DOWNLOAD/baci/doc/FAQ_BACI.html#7_Is_there_data_for_Taiwan , https://groups.google.com/g/witsforum/c/gXaRZfScejg
    "COP": {"Include": True, "IMF_NEER":  "COL", "BIS_NEER": "CO", "IMF_DOTS": "COL", "UNCT": 170, "BIS_FX": "CO", "BIS_FX_DOM": "COP"}, # Colombian peso
    "EUR": {"Include": True, "IMF_NEER": "G163", "BIS_NEER": "XM", "IMF_DOTS":"G163", "UNCT":  97, "BIS_FX": "XM", "BIS_FX_DOM": "EUR"},
    "CZK": {"Include": True, "IMF_NEER":  "CZE", "BIS_NEER": "CZ", "IMF_DOTS": "CZE", "UNCT": 203, "BIS_FX": "CZ", "BIS_FX_DOM": "CZK"}, # Czech Koruna
    "DKK": {"Include": True, "IMF_NEER":  "DNK", "BIS_NEER": "DK", "IMF_DOTS": "DNK", "UNCT": 208, "BIS_FX": "DK", "BIS_FX_DOM": "DKK"},
    "HKD": {"Include": True, "IMF_NEER":  "HKG", "BIS_NEER": "HK", "IMF_DOTS": "HKG", "UNCT": 344, "BIS_FX": "HK", "BIS_FX_DOM": "HKD"},
    "HUF": {"Include": True, "IMF_NEER":  "HUN", "BIS_NEER": "HU", "IMF_DOTS": "HUN", "UNCT": 348, "BIS_FX": "HU", "BIS_FX_DOM": "HUF"}, # Hungary forint
    "ISK": {"Include": True, "IMF_NEER":  "ISL", "BIS_NEER": "IS", "IMF_DOTS": "ISL", "UNCT": 352, "BIS_FX": "IS", "BIS_FX_DOM": "ISK"}, # Iceland Krona
    "INR": {"Include": True, "IMF_NEER":   None, "BIS_NEER": "IN", "IMF_DOTS": "IND", "UNCT": 699, "BIS_FX": "IN", "BIS_FX_DOM": "INR"},
    "IDR": {"Include": True, "IMF_NEER":   None, "BIS_NEER": "ID", "IMF_DOTS": "IDN", "UNCT": 360, "BIS_FX": "ID", "BIS_FX_DOM": "IDR"},
    "ILS": {"Include": True, "IMF_NEER":  "ISR", "BIS_NEER": "IL", "IMF_DOTS": "ISR", "UNCT": 376, "BIS_FX": "IL", "BIS_FX_DOM": "ILS"}, # Israeli shekel
    "JPY": {"Include": True, "IMF_NEER":  "JPN", "BIS_NEER": "JP", "IMF_DOTS": "JPN", "UNCT": 392, "BIS_FX": "JP", "BIS_FX_DOM": "JPY"},
    "KRW": {"Include": True, "IMF_NEER":   None, "BIS_NEER": "KR", "IMF_DOTS": "KOR", "UNCT": 410, "BIS_FX": "KR", "BIS_FX_DOM": "KRw"},
    "MYR": {"Include": True, "IMF_NEER":  "MYS", "BIS_NEER": "MY", "IMF_DOTS": "MYS", "UNCT": 458, "BIS_FX": "MY", "BIS_FX_DOM": "MYR"},
    "MXN": {"Include": True, "IMF_NEER":  "MEX", "BIS_NEER": "MX", "IMF_DOTS": "MEX", "UNCT": 484, "BIS_FX": "MX", "BIS_FX_DOM": "MXN"},
    "NZD": {"Include": True, "IMF_NEER":  "NZL", "BIS_NEER": "NZ", "IMF_DOTS": "NZL", "UNCT": 554, "BIS_FX": "NZ", "BIS_FX_DOM": "NZD"},
    "NOK": {"Include": True, "IMF_NEER":  "NOR", "BIS_NEER": "NO", "IMF_DOTS": "NOR", "UNCT": 579, "BIS_FX": "NO", "BIS_FX_DOM": "NOK"}, # Nowegian Krone
    "PEN": {"Include": True, "IMF_NEER":   None, "BIS_NEER": "PE", "IMF_DOTS": "PER", "UNCT": 604, "BIS_FX": "PE", "BIS_FX_DOM": "PEN"}, # Peru sol
    "PHP": {"Include": True, "IMF_NEER":  "PHL", "BIS_NEER": "PH", "IMF_DOTS": "PHL", "UNCT": 608, "BIS_FX": "PH", "BIS_FX_DOM": "PHP"},
    "PKR": {"Include": True, "IMF_NEER":  "PAK", "BIS_NEER": None, "IMF_DOTS": "PAK", "UNCT": 586, "BIS_FX": "PK", "BIS_FX_DOM": "PKR"}, # Pakistan rupee
    "PLN": {"Include": True, "IMF_NEER":  "POL", "BIS_NEER": "PL", "IMF_DOTS": "POL", "UNCT": 616, "BIS_FX": "PL", "BIS_FX_DOM": "PLN"}, # Polish Zloty
    "RON": {"Include": True, "IMF_NEER":  "ROU", "BIS_NEER": "RO", "IMF_DOTS": "ROU", "UNCT": 642, "BIS_FX": "RO", "BIS_FX_DOM": "RON"}, # Romanian Leu
    "RUB": {"Include": True, "IMF_NEER":  "RUS", "BIS_NEER": "RU", "IMF_DOTS": "RUS", "UNCT": 643, "BIS_FX": "RU", "BIS_FX_DOM": "RUB"},
    "SAR": {"Include": True, "IMF_NEER":  "SAU", "BIS_NEER": "SA", "IMF_DOTS": "SAU", "UNCT": 682, "BIS_FX": "SA", "BIS_FX_DOM": "SAR"}, # Saudi Riyal
    "SGD": {"Include": True, "IMF_NEER":  "SGP", "BIS_NEER": "SG", "IMF_DOTS": "SGP", "UNCT": 702, "BIS_FX": "SG", "BIS_FX_DOM": "SGD"},
    "ZAR": {"Include": True, "IMF_NEER":  "ZAF", "BIS_NEER": "ZA", "IMF_DOTS": "ZAF", "UNCT": 710, "BIS_FX": "ZA", "BIS_FX_DOM": "ZAR"},
    "SEK": {"Include": True, "IMF_NEER":  "SWE", "BIS_NEER": "SE", "IMF_DOTS": "SWE", "UNCT": 752, "BIS_FX": "SE", "BIS_FX_DOM": "SEK"}, # Sweden Krona
    "CHF": {"Include": True, "IMF_NEER":  "CHE", "BIS_NEER": "CH", "IMF_DOTS": "CHE", "UNCT": 756, "BIS_FX": "CH", "BIS_FX_DOM": "CHF"},
    "THB": {"Include": True, "IMF_NEER":   None, "BIS_NEER": "TH", "IMF_DOTS": "THA", "UNCT": 764, "BIS_FX": "TH", "BIS_FX_DOM": "THB"},
    "TRY": {"Include": True, "IMF_NEER":   None, "BIS_NEER": "TR", "IMF_DOTS": "TUR", "UNCT": 792, "BIS_FX": "TR", "BIS_FX_DOM": "TRY"},
    "AED": {"Include": True, "IMF_NEER":  "ARE", "BIS_NEER": "AE", "IMF_DOTS": "ARE", "UNCT": 784, "BIS_FX": "AE", "BIS_FX_DOM": "AED"},
    "GBP": {"Include": True, "IMF_NEER":  "GBR", "BIS_NEER": "GB", "IMF_DOTS": "GBR", "UNCT": 826, "BIS_FX": "GB", "BIS_FX_DOM": "GBP"},
    "USD": {"Include": True, "IMF_NEER":  "USA", "BIS_NEER": "US", "IMF_DOTS": "USA", "UNCT": 840, "BIS_FX": "US", "BIS_FX_DOM": "USD"},
    "VEF": {"Include": True, "IMF_NEER":   None, "BIS_NEER": "VE", "IMF_DOTS": "VEN", "UNCT": 862, "BIS_FX": "VE", "BIS_FX_DOM": "VEF"}, # Venezuelan Bolivar
    "VND": {"Include": True, "IMF_NEER":   None, "BIS_NEER": None, "IMF_DOTS": "VNM", "UNCT": 704, "BIS_FX": None, "BIS_FX_DOM":  None},
}

ns = {
    'mes': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message',
    'gen': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic',
    'ns1': 'urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:WS_XRU(1.0):compact',
}
