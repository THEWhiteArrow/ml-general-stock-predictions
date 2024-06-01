import datetime
from data import load_output, load_scraped_stocks
from gsp.publisher.transform import (
    transform_to_generation,
    transform_to_histories,
    transform_to_predictions,
    transform_to_stocks,
)
from lib.logger.setup import setup_logger

logger = setup_logger(__name__)


def run(run_date: datetime.date):
    logger.info("Starting the publisher...")
    # --- LOAD DATA ---
    stocks_df = load_scraped_stocks()
    generation_df = load_output(f"generation_{run_date.isoformat()}.csv")
    prediction_df = load_output(f"prediction_{run_date.isoformat()}.csv")

    # --- DATA PREPARATION ---
    logger.info("Transforming data...")
    generation = transform_to_generation(generation_df)
    predictions = transform_to_predictions(prediction_df)
    stocks = transform_to_stocks(stocks_df)
    histories = transform_to_histories(stocks_df)

    # --- PUBLISH DATA ---
    logger.info("Publishing data...")

    logger.info("Publishing finished successfully")


if __name__ == "__main__":
    # run_date = datetime.date.today()
    run_date = datetime.date(year=2024, month=5, day=31)
    run(run_date=run_date)
