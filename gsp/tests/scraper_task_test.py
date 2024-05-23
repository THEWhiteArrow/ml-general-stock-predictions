import json
import os
import pandas as pd
import pytest
from gsp.scraper.scraper import gather_stocks_data, gather_traded_stocks_list
from data import SCRAPED_STOCK_FILE_PATH, SCRAPED_TRADED_STOCK_LIST_FILE_PATH, SETUP_STOCK_FILE_PATH, SETUP_STOCK_ALIAS
import logging

logger = logging.getLogger(__name__)


def test_scraper_task_downlaods_and_saves_stocks_history():
    """Tests if the scraper task downloads and saves stock history."""

    # --- ACT ---
    gather_stocks_data()

    # --- ASSERT ---
    if os.path.exists(SCRAPED_STOCK_FILE_PATH):
        assert True
    else:
        pytest.fail("Path to scraped stocks file is incorrect : " + SCRAPED_STOCK_FILE_PATH)


def test_scraper_task_downloads_and_save_traded_stocks_list():
    """Tests if the scraper task downloads and saves traded stocks list."""

    # --- ACT ---
    gather_traded_stocks_list()

    # --- ASSERT ---
    if os.path.exists(SCRAPED_TRADED_STOCK_LIST_FILE_PATH):
        assert True
    else:
        pytest.fail("Path to scraped traded stocks list file is incorrect : " + SCRAPED_TRADED_STOCK_LIST_FILE_PATH)


@pytest.mark.skip(reason="There are companies that are not traded on NASDAQ but list is only for NASDAQ.")
def test_setup_stocks_json_is_valid():
    """Tests if the setup stocks json file is valid (has the exisiting publicly traded companies)."""

    # --- SETUP ---
    stocks_setup: SETUP_STOCK_ALIAS = json.load(open(SETUP_STOCK_FILE_PATH, "r"))

    # --- ACT ---
    gather_stocks_data()

    # --- ASSERT ---
    traded_stocks_df = pd.read_csv(SCRAPED_TRADED_STOCK_LIST_FILE_PATH)
    for area in stocks_setup:
        for stock_company in stocks_setup[area]:
            assert stock_company["stock_id"] in traded_stocks_df["symbol"].values
