import os
import pytest
from gsp.scraper.run import run
from data import SCRAPED_STOCK_FILE_PATH
import logging

logger = logging.getLogger(__name__)


def test_scraper_task_downlaods_and_saves_stoch_history():
    """Tests if the scraper task downloads and saves stock history."""

    # --- ACT ---
    run()

    # --- ASSERT ---
    if os.path.exists(SCRAPED_STOCK_FILE_PATH):
        assert True
    else:
        pytest.fail("Path to scraped stocks file is incorrect : " + SCRAPED_STOCK_FILE_PATH)
