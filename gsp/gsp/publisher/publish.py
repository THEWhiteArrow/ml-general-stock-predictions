import datetime
from typing import List
from generated.generation import Generation
from generated.stock import Stock
from gsp.mongodb.stock_ref_mapping import StockRefMapping
from gsp.mongodb.storage_collections import StorageCollections
from gsp.mongodb.storage_helper import StorageHelper


def publish_data(
    run_date: datetime.date,
    stocks: List[Stock],
    histories: StockRefMapping,
    generation: Generation,
    predictions: StockRefMapping,
):
    """A function that handles publishing the data to the database.
    If the stock is not in the database, it will be inserted alonside its history.
    If the stock is already in the database, the newest history will be added.
    Generation and predictions will be inserted as is.
    """
    storage_helper = StorageHelper()

    stocks_in_db = storage_helper.load_collection_documents(StorageCollections.STOCKS)
    stocks_symbols_in_db = [stock["symbol"] for stock in stocks_in_db]

    stocks_not_in_db: List[Stock] = [stock for stock in stocks if stock.symbol not in stocks_symbols_in_db]
    if len(stocks_not_in_db) > 0:
        storage_helper.insert_documents(StorageCollections.STOCKS, [stock.to_dict() for stock in stocks_not_in_db])
        not_in_db_mapping = StockRefMapping()
        for stock in stocks_not_in_db:
            not_in_db_mapping.add(stock.symbol, histories.get_by_symbol(stock.symbol))
        storage_helper.add_histories(not_in_db_mapping)

    stocks_in_db_mapping = StockRefMapping()
    for stock in stocks_in_db:
        stocks_in_db_mapping.add(stock["symbol"], histories.get_by_symbol(stock["symbol"]))
        newest_histories = list(filter(lambda h: h.date == run_date, histories.get_by_symbol(stock["symbol"])))
        stocks_in_db_mapping.add(stock["symbol"], newest_histories)

    storage_helper.add_histories(stocks_in_db_mapping)

    storage_helper.add_generation_with_predictions(generation, predictions)
