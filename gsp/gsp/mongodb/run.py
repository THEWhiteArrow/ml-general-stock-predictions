from lib.logger.setup import setup_logger
from gsp.mongodb.storage_helper import StorageHelper
from generated.stock import Stock, History, Prediction

logger = setup_logger(__name__)


def run():
    logger.info("Running mongodb.run...")
    storage_helper = StorageHelper()

    storage_helper.setup_connection()
    # stocks_collection = storage_helper.load_collection("stocks2")
    # stocks_documents = storage_helper.load_collection_documents("stocks2", reference={"history": "histories"})

    amazon = Stock.from_dict(
        {
            "symbol": "AMZN",
            "company": "Amazon",
            "histories": [
                {"date": "2021-01-01", "open": 1000, "high": 1050, "low": 950, "close": 1025, "volume": 1000000}
            ],
            "predictions": [],
        }
    )
    google = Stock.from_dict(
        {
            "symbol": "GOOGL",
            "company": "Google",
            "histories": [
                {"date": "2021-01-01", "open": 1500, "high": 1550, "low": 1450, "close": 1525, "volume": 1000000}
            ],
            "predictions": [],
        }
    )
    storage_helper.delete_stocks()
    storage_helper.save_stocks([amazon, google])

    prediction = Prediction.from_dict(
        {
            "created_at": "2024-05-31",
            "date": "2024-06-01",
            "name": "testing prediction",
            "values": [
                {"value": 2222, "date": "2024-06-02"},
            ],
            "config": {
                "categorical_features": ["a", "b", "c"],
                "label_features": ["d", "e", "f"],
                "days_back_to_consider": 10,
                "mwms": [5, 10, 15],
                "shifts": [1, 2, 3],
                "n_step": 5,
                "hyper_params": {"a": 1, "b": 2, "c": 3},
            },
        }
    )

    storage_helper.add_predictions_to_stocks({"AMZN": [prediction]})

    logger.info("Closing connection...")
    storage_helper.close_connection()


if __name__ == "__main__":
    run()
