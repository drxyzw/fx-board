
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
    "DZD": {"Include": True, "IMF":   None, "BIS": "DZ", "DOTS": "DZA", "UNCT": 12}, # Algerian dinar
    "ARS": {"Include": True, "IMF":   None, "BIS": "AR", "DOTS": "ARG", "UNCT": 32}, # Argentina peso
    "AUD": {"Include": True, "IMF":  "AUS", "BIS": "AU", "DOTS": "AUS", "UNCT": 36},
    "BDT": {"Include": True, "IMF":   None, "BIS": None, "DOTS": "BGD", "UNCT": 50}, # Bangladesh taka
    "BRL": {"Include": True, "IMF":  "BRA", "BIS": "BR", "DOTS": "BRA", "UNCT": 76},
    "KHR": {"Include": True, "IMF":   None, "BIS": None, "DOTS": "KHN", "UNCT": 116}, # Cambodian riel
    "CAD": {"Include": True, "IMF":  "CAN", "BIS": "CA", "DOTS": "CAN", "UNCT": 124},
    "CLP": {"Include": True, "IMF":  "CHL", "BIS": "CL", "DOTS": "CHL", "UNCT": 152}, # Chilean peso
    "CNY": {"Include": True, "IMF":  "CHN", "BIS": "CN", "DOTS": "CHN", "UNCT": 156},
    "NTD": {"Include": True, "IMF":   None, "BIS": "TW", "DOTS": "TWN", "UNCT": 490}, # https://www.cepii.fr/DATA_DOWNLOAD/baci/doc/FAQ_BACI.html#7_Is_there_data_for_Taiwan , https://groups.google.com/g/witsforum/c/gXaRZfScejg
    "COP": {"Include": True, "IMF":  "COL", "BIS": "CO", "DOTS": "COL", "UNCT": 170}, # Colombian peso
    "EUR": {"Include": True, "IMF": "G163", "BIS": "XM", "DOTS": "G995","UNCT": 97},
    "CZK": {"Include": True, "IMF":  "CZE", "BIS": "CZ", "DOTS": "CZE", "UNCT": 203}, # Czech Koruna
    "DKK": {"Include": True, "IMF":  "DNK", "BIS": "DK", "DOTS": "DNK", "UNCT": 208},
    "HKD": {"Include": True, "IMF":  "HKG", "BIS": "HK", "DOTS": "HKG", "UNCT": 344},
    "HUF": {"Include": True, "IMF":  "HUN", "BIS": "HU", "DOTS": "HUN", "UNCT": 348}, # Hungary forint
    "ISK": {"Include": True, "IMF":  "ISL", "BIS": "IS", "DOTS": "ISL", "UNCT": 352}, # Iceland Krona
    "INR": {"Include": True, "IMF":   None, "BIS": "IN", "DOTS": "IND", "UNCT": 699},
    "IDR": {"Include": True, "IMF":   None, "BIS": "ID", "DOTS": "IDN", "UNCT": 360},
    "ILS": {"Include": True, "IMF":  "ISR", "BIS": "IL", "DOTS": "ISR", "UNCT": 376}, # Israeli shekel
    "JPY": {"Include": True, "IMF":  "JPN", "BIS": "JP", "DOTS": "JPN", "UNCT": 392},
    "KRW": {"Include": True, "IMF":   None, "BIS": "KR", "DOTS": "KOR", "UNCT": 410},
    "MYR": {"Include": True, "IMF":  "MYS", "BIS": "MY", "DOTS": "MYS", "UNCT": 458},
    "MXN": {"Include": True, "IMF":  "MEX", "BIS": "MX", "DOTS": "MEX", "UNCT": 484},
    "NZD": {"Include": True, "IMF":  "NZL", "BIS": "NZ", "DOTS": "NZL", "UNCT": 554},
    "NOK": {"Include": True, "IMF":  "NOR", "BIS": "NO", "DOTS": "NOR", "UNCT": 579}, # Nowegian Krone
    "PEN": {"Include": True, "IMF":   None, "BIS": "PE", "DOTS": "PER", "UNCT": 604}, # Peru sol
    "PHP": {"Include": True, "IMF":  "PHL", "BIS": "PH", "DOTS": "PHL", "UNCT": 608},
    "PKR": {"Include": True, "IMF":  "PAK", "BIS": None, "DOTS": "PAK", "UNCT": 586}, # Pakistan rupee
    "PLZ": {"Include": True, "IMF":  "POL", "BIS": "PL", "DOTS": "POL", "UNCT": 616}, # Polish Zloty
    "RON": {"Include": True, "IMF":  "ROU", "BIS": "RO", "DOTS": "ROU", "UNCT": 642}, # Romanian Leu
    "RUB": {"Include": True, "IMF":  "RUS", "BIS": "RU", "DOTS": "RUS", "UNCT": 643},
    "SAR": {"Include": True, "IMF":  "SAU", "BIS": "SA", "DOTS": "SAU", "UNCT": 682}, # Saudi Riyal
    "SGD": {"Include": True, "IMF":  "SGP", "BIS": "SG", "DOTS": "SGP", "UNCT": 702},
    "ZAR": {"Include": True, "IMF":  "ZAF", "BIS": "ZA", "DOTS": "ZAF", "UNCT": 710},
    "SEK": {"Include": True, "IMF":  "SWE", "BIS": "SE", "DOTS": "SWE", "UNCT": 752}, # Sweden Krona
    "CHF": {"Include": True, "IMF":  "CHE", "BIS": "CH", "DOTS": "CHE", "UNCT": 756},
    "THB": {"Include": True, "IMF":   None, "BIS": "TH", "DOTS": "THA", "UNCT": 764},
    "TRY": {"Include": True, "IMF":   None, "BIS": "TR", "DOTS": "TUR", "UNCT": 792},
    "AED": {"Include": True, "IMF":  "ARE", "BIS": "AE", "DOTS": "ARE", "UNCT": 784},
    "GBP": {"Include": True, "IMF":  "GBR", "BIS": "GB", "DOTS": "GBR", "UNCT": 826},
    "USD": {"Include": True, "IMF":  "USA", "BIS": "US", "DOTS": "USA", "UNCT": 840},
    "VEF": {"Include": True, "IMF":   None, "BIS": "VE", "DOTS": "VEN", "UNCT": 862}, # Venezuelan Bolivar
    "VND": {"Include": True, "IMF":   None, "BIS": None, "DOTS": "VNM", "UNCT": 704},
}
