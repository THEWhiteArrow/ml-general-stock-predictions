import datetime
from typing import List
from data import load_output, load_scraped_stocks
import pandas as pd
from generated.stock import Stock
from generated.generation import Generation
from generated.history import History
from generated.prediction import Prediction
from lib.logger.setup import setup_logger

logger = setup_logger(__name__)


def run(run_date: datetime.date):
    logger.info("Starting the publisher...")
    # --- LOAD DATA ---
    stocks_df = load_scraped_stocks()
    generation_df = load_output(f"generation_{run_date.isoformat()}.csv")
    prediction_df = load_output(f"prediction_{run_date.isoformat()}.csv")
    generation_data = generation_df.head(1).to_dict(orient="records")[0]
    prediction_data = prediction_df.to_dict(orient="records")
    stocks_data = stocks_df.to_dict(orient="records")

    # --- DATA PREPARATION ---
    generation: Generation
    predictions: List[Prediction]
    stocks: List[Stock]
    histories: List[History]

    # --- TODO: fix this ---
    generation_data["prediction_date"]
    generation = Generation.from_dict(generation_data)
    predictions = [Prediction.from_dict(prediction) for prediction in prediction_data]
    stocks = [Stock.from_dict(stock) for stock in stocks_data]
    histories = [History.from_dict(stock) for stock in stocks_data]

    logger.info("Data transformed successfully")


if __name__ == "__main__":
    run_date = datetime.date.today()
    # run_date = datetime.date(year=2024, month=5, day=24)
    run(run_date=run_date)
