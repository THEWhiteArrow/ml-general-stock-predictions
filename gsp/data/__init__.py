import os
from typing import Dict, List, Literal

SCRAPED_DIR: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "scraped")
SETUP_STOCK_FILE_PATH: str = os.path.join(os.path.abspath(os.path.dirname(__file__)), "setup", "stocks_setup.json")

SETUP_STOCK_COMPANY_ALIAS = Dict[Literal["company_name"] | Literal["stock_id"], str]
SETUP_STOCK_ALIAS = Dict[str, List[SETUP_STOCK_COMPANY_ALIAS]]
