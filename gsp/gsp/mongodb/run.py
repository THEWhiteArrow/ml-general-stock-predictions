# import datetime
# from gsp.mongodb.stock_ref_mapping import StockRefMapping
from gsp.mongodb.storage_helper import StorageHelper

# from generated.history import History
from lib.logger.setup import setup_logger

logger = setup_logger(__name__)


def run():

    # history = History.from_dict(
    #     {
    #         "name": "History",
    #         "date": "2024-06-01",
    #         "stock": "665e16b431b317cf141e8175",
    #         "volume": 1000,
    #         "high": 100.0,
    #         "low": 100.0,
    #         "open": 100.0,
    #         "close": 100.0,
    #     }
    # )
    # logger.info(f"History: {history.to_dict()}")

    storage_helper = StorageHelper()
    storage_helper.setup_connection()
    storage_helper.cleanse("v2")

    # mapping = StockRefMapping()
    # mapping.add("GOOGL", [history])
    # storage_helper.add_histories(mapping)
    # storage_helper.close_connection()

    # logger.info(storage_helper.exists_history_for_date(datetime.date(2024, 6, 1)))
    logger.info("Code above is created for debugging purposes.")


if __name__ == "__main__":
    run()
