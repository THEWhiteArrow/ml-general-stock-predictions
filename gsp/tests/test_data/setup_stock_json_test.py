import json
from data import SETUP_STOCK_FILE_PATH, SETUP_STOCK_ALIAS


def test_setup_stock_contains_no_duplicate_companies():
    duplicated_companies = {}
    stock_setup: SETUP_STOCK_ALIAS = json.load(open(SETUP_STOCK_FILE_PATH, "r"))
    for area in stock_setup:
        for stock_company in stock_setup[area]:
            if stock_company["stock_id"] in duplicated_companies:
                duplicated_companies[stock_company["stock_id"]] += 1
            else:
                duplicated_companies[stock_company["stock_id"]] = 1

    duplicated_companies = {k: v for k, v in duplicated_companies.items() if v > 1}
    assert not duplicated_companies, f"Duplicate companies found: {duplicated_companies}"
