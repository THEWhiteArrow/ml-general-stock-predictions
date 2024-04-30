import json
import pandas as pd
import io
import logging
from gsp.scraper.download import download_from_yahoo_api
from data import SETUP_STOCK_FILE_PATH, SCRAPED_DIR, SETUP_STOCK_ALIAS

logger = logging.getLogger(__name__)


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
    stock_data_df = pd.DataFrame()

    for area in stock_setup:
        for stock_company in stock_setup[area]:
            data = download_from_yahoo_api(stock_id=stock_company["stock_id"])

            df = pd.read_csv(io.StringIO(data))
            df["Area"] = area
            df["Name"] = stock_company["stock_id"]

            stock_data_df = pd.concat([stock_data_df, df], axis=0)

    stock_data_df.to_csv(f"{SCRAPED_DIR}/stock_data.csv")
    logger.info("Data saved successfully")


run()
