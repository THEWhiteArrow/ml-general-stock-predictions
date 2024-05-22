from typing import Dict
import requests
import datetime
from lib.logger.setup import setup_logger

logger = setup_logger()


def download_stocks_history_from_yahoo_api(
    stock_id: str,
) -> str:
    url = f"https://query1.finance.yahoo.com/v7/finance/download/{stock_id}"

    response = requests.get(
        url=url,
        params={
            "period1": "0",
            "period2": int(datetime.datetime.now().timestamp()),
        },
        headers={
            "Accept": "text/csv",
            "User-Agent": "Mozilla/5.0",
        },
        timeout=5,
    )
    if response.status_code == 200:
        data = response.text
        logger.info(f"Downloaded yahoo finance history: {stock_id}")
        return data

    else:
        raise Exception(
            f"An error occurred while downloading {stock_id} stocks history. Status code: {response.status_code}"
        )


def download_traded_stocks_list_from_nasdaq_api() -> Dict:
    url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&download=true"
    response = requests.get(
        url=url,
        headers={
            "Accept": "text/csv",
            "User-Agent": "Mozilla/5.0",
        },
        timeout=5,
    )

    if response.status_code == 200:
        data = response.json()
        logger.info("Downloaded traded stocks list from NASDAQ")
        return data

    else:
        raise Exception(
            f"An error occurred while downloading traded stocks list from NASDAQ. Status code: {response.status_code}"
        )
