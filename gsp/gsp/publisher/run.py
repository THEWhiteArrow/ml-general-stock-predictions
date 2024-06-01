import datetime
from data import load_output, load_scraped_stocks
from gsp.publisher.publish import publish_data
from gsp.publisher.transform import (
    transform_generation,
    transform_histories,
    transform_predictions,
    transform_stocks,
)
from lib.logger.setup import setup_logger
import pickle

logger = setup_logger(__name__)


def run(run_date: datetime.date):
    logger.info("Starting the publisher...")
    # --- LOAD DATA ---
    stocks_df = load_scraped_stocks()
    generation_df = load_output(f"generation_{run_date.isoformat()}.csv")
    prediction_df = load_output(f"prediction_{run_date.isoformat()}.csv")

    # --- DATA PREPARATION ---
    logger.info("Transforming data...")

    # --- NOTE: CACHING ---
    # ->> For development and debugging purposes only, ->> remove in production
    try:
        with open("cache.pkl", "rb") as f:
            cache = pickle.load(f)
            stocks = cache["stocks"]
            generation = cache["generation"]
            predictions_mapping = cache["predictions_mapping"]
            histories_mapping = cache["histories_mapping"]
    except FileNotFoundError:
        stocks = transform_stocks(stocks_df)
        generation = transform_generation(generation_df)
        predictions_mapping = transform_predictions(prediction_df)
        histories_mapping = transform_histories(stocks_df)

        # store generation, predictions, stocks and histores in a cache
        cache = {
            "stocks": stocks,
            "generation": generation,
            "predictions_mapping": predictions_mapping,
            "histories_mapping": histories_mapping,
        }

        # save the cache
        with open("cache.pkl", "wb") as f:
            pickle.dump(cache, f)

    # --- PUBLISH DATA ---
    logger.info("Publishing data...")
    publish_data(run_date, stocks, histories_mapping, generation, predictions_mapping)

    logger.info("Publishing finished successfully")


if __name__ == "__main__":
    # run_date = datetime.date.today()
    run_date = datetime.date(year=2024, month=5, day=31)
    run(run_date=run_date)
