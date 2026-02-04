
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
