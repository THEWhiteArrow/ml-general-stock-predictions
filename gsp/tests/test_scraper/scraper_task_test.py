import datetime
import io
import os
import pandas as pd
import pytest
from gsp.scraper.run import scrape
from gsp.scraper.download import download_stocks_history_from_yahoo_api
from data import SCRAPED_STOCK_FILE_PATH
import logging

logger = logging.getLogger(__name__)


def test_download_stocks_history_from_yahoo_api_get_data_successfully():
    """Tests if the function downloads stock history data from Yahoo API successfully."""

    # --- SETUP ---
    stock_id = "AAPL"

    # --- ACT ---
    data = download_stocks_history_from_yahoo_api(stock_id=stock_id, end_date=datetime.date.today())
    df = pd.read_csv(io.StringIO(data))

    # --- ASSERT ---
    columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
    assert not df.empty
    assert all([column in df.columns for column in columns])


@pytest.mark.skip(reason="It executes entire scraping process which is too long for a test.")
def test_scraper_task_downlaods_and_saves_stocks_history():
    """Tests if the scraper task downloads and saves stock history."""

    # --- ACT ---
    scrape(datetime.date.today())

    # --- ASSERT ---
    if os.path.exists(SCRAPED_STOCK_FILE_PATH):
        assert True
    else:
        pytest.fail("Path to scraped stocks file is incorrect : " + SCRAPED_STOCK_FILE_PATH)
