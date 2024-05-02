import pytest
import os
from data import SETUP_STOCK_FILE_PATH, SCRAPED_STOCK_FILE_PATH


def test_data_path_setup_json_correctly_loads():
    if os.path.exists(SETUP_STOCK_FILE_PATH):
        assert True
    else:
        pytest.fail("Path to setup json file is incorrect : " + SETUP_STOCK_FILE_PATH)


def test_data_path_scraped_stocks_correctly_loads():
    if os.path.exists(SCRAPED_STOCK_FILE_PATH):
        assert True
    else:
        pytest.fail("Path to scraped stocks file is incorrect : " + SCRAPED_STOCK_FILE_PATH)
