import datetime
from data import load_output, load_scraped_stocks
from generated.stock import Stock
from gsp.mongodb.stock_ref_mapping import StockRefMapping
from gsp.mongodb.storage_collections import StorageCollections
from gsp.mongodb.storage_helper import StorageHelper
from gsp.publisher.transform import (
    transform_generation,
    transform_histories,
    transform_predictions,
    transform_stocks,
)
from gsp.utils.date_utils import get_nth_previous_working_date
from lib.logger.setup import setup_logger

# import pickle

logger = setup_logger(__name__)


def run(run_date: datetime.date):
    logger.info("Starting the publisher...")
    # --- LOAD DATA ---
    stocks_df = load_scraped_stocks()
    generation_df = load_output(f"generation_{run_date.isoformat()}.csv")
    prediction_df = load_output(f"prediction_{run_date.isoformat()}.csv")

    # --- DATA PREPARATION ---
    logger.info("Transforming data...")

    stocks = transform_stocks(stocks_df)
    generation = transform_generation(generation_df)
    predictions_mapping = transform_predictions(prediction_df)
    # histories_mapping = transform_histories(stocks_df)

    # --- PUBLISH DATA ---
    logger.info("Publishing data...")

    # histories = histories.filter_by_date(start_date=None, end_date=run_date)

    storage_helper = StorageHelper()

    loaded_stocks_dicts = storage_helper.load_collection_documents(StorageCollections.STOCKS)
    loaded_stocks = [Stock.from_dict({**stock, "_id": str(stock["_id"])}) for stock in loaded_stocks_dicts]
    loaded_stock_symbols = [stock.symbol for stock in loaded_stocks]

    stocks_not_in_db = [stock for stock in stocks if stock.symbol not in loaded_stock_symbols]
    stocks_in_db = [stock for stock in stocks if stock.symbol in loaded_stock_symbols]

    if len(stocks_not_in_db) > 0:
        storage_helper.insert_documents(StorageCollections.STOCKS, [stock.to_dict() for stock in stocks_not_in_db])
        not_in_db_mapping = StockRefMapping()
        histories = transform_histories(
            stocks_df, [stock.symbol for stock in stocks_not_in_db], start_date=None, end_date=run_date
        )
        for stock in stocks_not_in_db:
            not_in_db_mapping.add(stock.symbol, histories.get_by_symbol(stock.symbol))
        storage_helper.add_histories(not_in_db_mapping)

    if len(stocks_in_db) > 0:
        latest_history_date = storage_helper.get_latest_history_date()
        if latest_history_date is not None:
            latest_history_date = get_nth_previous_working_date(-1, latest_history_date)
        else:
            latest_history_date = run_date

        stocks_in_db_new_histories = transform_histories(
            stocks_df, [stock.symbol for stock in stocks_in_db], start_date=latest_history_date, end_date=run_date
        )
        stocks_in_db_mapping = StockRefMapping()

        for stock in stocks_in_db:
            stocks_in_db_mapping.add(stock.symbol, stocks_in_db_new_histories.get_by_symbol(stock.symbol))

        storage_helper.add_histories(stocks_in_db_mapping)

    if storage_helper.exists_generation(date=run_date, name=generation.name):
        logger.warning(f"Generation for date {run_date} and name {generation.name} already exists in the database")
    else:
        storage_helper.add_generation_with_predictions(generation, predictions_mapping)

    logger.info("Publishing finished successfully")


if __name__ == "__main__":
    run_date = datetime.date.today()
    # run_date = datetime.date(year=2024, month=1, day=1)
    # run_date = datetime.date(year=2024, month=1, day=2)
    # run_date = datetime.date(year=2024, month=1, day=3)
    # run_date = datetime.date(year=2024, month=6, day=11)
    run(run_date=run_date)
