import json
from gsp.scraper.download import download_from_yahoo_api
from data import SETUP_STOCK_FILE_PATH, SCRAPED_DIR, SETUP_STOCK_ALIAS


def run():
    """
    The following code snippet has one aim: to download data that is used in the Machine Learning model.
    The data that is being downloaded is up-to-date meaning
    that it is possible to automate the process of downloading the data.
    It possibly means that the project could be run every day with the help
    of a scheduler and provide the most recent data and predictions.

    The code snippet is a part of the run.py file that is located in the nsp/scraper directory.
    """
    stock_setup: SETUP_STOCK_ALIAS = json.load(open(SETUP_STOCK_FILE_PATH, "r"))

    for category in stock_setup:
        for stock_company in stock_setup[category]:
            download_from_yahoo_api(stock_id=stock_company["stock_id"], save_dir=SCRAPED_DIR)


run()
