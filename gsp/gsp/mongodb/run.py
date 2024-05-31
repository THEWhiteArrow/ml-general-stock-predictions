from gsp.mongodb.stock_ref_mapping import StockRefMapping
from lib.logger.setup import setup_logger
from gsp.mongodb.storage_helper import StorageHelper
from generated.stock import Stock
from generated.prediction import Prediction
from generated.history import History
from generated.generation import Generation

logger = setup_logger(__name__)


def run():
    logger.info("Running mongodb.run...")
    storage_helper = StorageHelper()

    storage_helper.setup_connection()

    amazon = Stock.from_dict(
        {
            "symbol": "AMZN",
            "company": "Amazon",
        }
    )
    google = Stock.from_dict(
        {
            "symbol": "GOOGL",
            "company": "Google",
        }
    )
    some_generation = Generation.from_dict(
        {
            "created_at": "2024-05-31",
            "date": "2024-06-01",
            "name": "testing generation",
            "categorical_features": ["a", "b", "c"],
            "label_features": ["d", "e", "f"],
            "days_back_to_consider": 10,
            "mwms": [5, 10, 15],
            "shifts": [1, 2, 3],
            "n_step": 5,
            "hyper_params": {"a": 1, "b": 2, "c": 3},
        }
    )
    amazon_prediction = Prediction.from_dict(
        {
            "date": "2024-06-03",
            "close": 1234.56,
        }
    )
    google_history = History.from_dict(
        {
            "date": "2024-06-01",
            "close": 1234.56,
            "high": 1234.56,
            "low": 1234.56,
            "open": 1234.56,
            "volume": 123456,
        }
    )

    storage_helper.cleanse(pattern="v2")

    history_mapping = StockRefMapping().add_stock("GOOGL", [google_history]).add_stock("AMZN", [])
    prediction_mapping = StockRefMapping().add_stock("GOOGL", []).add_stock("AMZN", [amazon_prediction])

    storage_helper.save_stocks([amazon, google])
    storage_helper.add_histories(history_mapping)
    storage_helper.add_generation_with_predictions(some_generation, prediction_mapping)

    logger.info("Closing connection...")
    storage_helper.close_connection()


if __name__ == "__main__":
    run()
