import datetime
from data import load_output
from lib.logger.setup import setup_logger
from gsp.utils.date_utils import get_nth_previous_working_date
from gsp.mongodb.setup import setup_mongodb, setup_collection, setup_database
from gsp.mongodb.transformation import transform_generation_predictions_to_mongodb_documents

logger = setup_logger(__name__)


def publish(prediction_date: datetime.date):
    logger.info("Setting up MongoDB connection...")
    client = setup_mongodb()

    logger.info("Setting up MongoDB database...")
    database = setup_database(client)

    logger.info("Setting up MongoDB collections...")
    generations_collection = setup_collection(database, "generations")
    predictions_collection = setup_collection(database, "predictions")

    logger.info("Loading dataframes...")
    generation_df = load_output(f"generation_{prediction_date.isoformat()}.csv")
    prediction_df = load_output(f"prediction_{prediction_date.isoformat()}.csv")

    logger.info("Transforming dataframes into mongodb documents...")
    generation_doc, prediction_doc = transform_generation_predictions_to_mongodb_documents(
        generation_df=generation_df,
        prediction_df=prediction_df,
    )

    logger.info("Inserting documents into MongoDB collections...")
    generations_collection.insert_many(generation_doc)
    predictions_collection.insert_many(prediction_doc)

    logger.info("Closing MongoDB connection...")
    client.close()


if __name__ == "__main__":
    prediction_date = get_nth_previous_working_date(n=0, date=datetime.date.today())
    publish(prediction_date=prediction_date)
