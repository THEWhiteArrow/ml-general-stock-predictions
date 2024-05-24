import datetime
from data import load_output
from gsp.mongodb.crud import save_generation_predictions_to_mongodb
from lib.logger.setup import setup_logger
from gsp.utils.date_utils import get_nth_previous_working_date
from gsp.mongodb.setup import setup_mongodb, setup_collection
from gsp.mongodb.transformation import transform_generation_predictions_to_mongodb_documents

logger = setup_logger(__name__)


def publish(prediction_date: datetime.date):
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

    logger.info("Saving data to MongoDB...")
    save_generation_predictions_to_mongodb(generation_doc, predictions_doc)

    logger.info("Successfully saved data to MongoDB!")


if __name__ == "__main__":
    prediction_date = get_nth_previous_working_date(n=0, date=datetime.date.today())
    publish(prediction_date=prediction_date)
