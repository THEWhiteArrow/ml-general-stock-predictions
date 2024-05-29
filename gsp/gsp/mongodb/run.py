import datetime
from data import load_output, SCRAPED_STOCK_FILE_PATH
from gsp.mongodb.crud import (
    save_generation_predictions_to_mongodb,
    save_stocks_history_to_mongodb,
)
from lib.logger.setup import setup_logger
from gsp.utils.date_utils import get_nth_previous_working_date
from gsp.mongodb.setup import setup_mongodb, setup_collection
from gsp.mongodb.transformation import (
    transform_generation_predictions_to_mongodb_documents,
    transform_stocks_to_mongodb_documents,
)
import pandas as pd

logger = setup_logger(__name__)


def publish_predictions(prediction_date: datetime.date):
    logger.info("Setting up MongoDB connection...")
    setup_mongodb()

    logger.info("Setting up MongoDB collections...")
    setup_collection("generations")
    setup_collection("predictions")

    logger.info("Loading output data...")
    generation_df = load_output(
        f"generation_{prediction_date.isoformat()}.csv",
        dtypes={
            "PredictionDate": "period[D]",
            "Name": "string",
            "CategoricalFeatures": "object",
            "LabelFeatures": "object",
            "ShiftList": "object",
            "MWMList": "object",
            "DaysBackToConsider": "int",
            "NSteps": "int",
            "HyperParams": "object",
        },
        parse_dates=["CreatedTimestamp"],
    )
    prediction_df = load_output(
        f"prediction_{prediction_date.isoformat()}.csv",
        dtypes={"Date": "period[D]", "Name": "string", "Close": "float"},
    )

    logger.info("Transforming dataframes into MongoDB documents...")
    generation_doc, predictions_doc = transform_generation_predictions_to_mongodb_documents(
        generation_df=generation_df, prediction_df=prediction_df
    )

    logger.info("Handling saving data to MongoDB...")
    save_generation_predictions_to_mongodb(generation_doc, predictions_doc)

    logger.info("Successfully saved data to MongoDB!")


def publish_history():
    logger.info("Setting up MongoDB connection...")
    setup_mongodb()

    logger.info("Setting up MongoDB collections...")
    setup_collection("stocks")
    setup_collection("histories")

    logger.info("Loading stocks data...")
    stocks = pd.read_csv(
        SCRAPED_STOCK_FILE_PATH,
        dtype={
            "Date": "period[D]",
            "Open": "float",
            "High": "float",
            "Low": "float",
            "Close": "float",
            "Volume": "int",
            "Area": "category",
            "Name": "category",
        },
    )

    logger.info("Transforming dataframes into MongoDB documents...")
    stocks_doc = transform_stocks_to_mongodb_documents(stocks)

    logger.info("Handling saving data to MongoDB...")
    save_stocks_history_to_mongodb(stocks_doc)

    logger.info("Successfully saved data to MongoDB!")


if __name__ == "__main__":
    prediction_date = get_nth_previous_working_date(n=0, date=datetime.date.today())
    publish_history()
    # publish_predictions(prediction_date=prediction_date)
