import io
import json
import pandas as pd
from lib.logger.setup import setup_logger
from gsp.scraper.download import download_stocks_history_from_yahoo_api
from data import (
    SETUP_STOCK_FILE_PATH,
    SETUP_STOCK_ALIAS,
    SCRAPED_STOCK_FILE_PATH,
)

logger = setup_logger()


def scrape():
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
            data = download_stocks_history_from_yahoo_api(stock_id=stock_company["stock_id"])

            df = pd.read_csv(
                io.StringIO(data),
                dtype={
                    "Date": "period[D]",
                    "Open": "float",
                    "High": "float",
                    "Low": "float",
                    "Close": "float",
                    "Volume": "int",
                },
            )

            df = df.rename(columns={col: col.lower().replace(" ", "_") for col in df.columns})

            df["area"] = area
            df["symbol"] = stock_company["stock_id"]
            df["company"] = stock_company["company_name"]

            stock_data_df = pd.concat([stock_data_df, df], axis=0)

    stock_data_df.to_csv(SCRAPED_STOCK_FILE_PATH, index=False)
    logger.info("Stocks data saved successfully")


if __name__ == "__main__":
    scrape()
