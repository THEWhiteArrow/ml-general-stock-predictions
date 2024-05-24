import os
from typing import Optional
from dotenv import load_dotenv
from lib.logger.setup import setup_logger
import mongoengine as me

logger = setup_logger(__name__)


def setup_mongodb():
    """Connect to MongoDB using the connection URI provided in the .env file."""
    load_dotenv()

    db_user: Optional[str] = os.getenv("DB_USER")
    db_password: Optional[str] = os.getenv("DB_PASSWORD")
    cluster_name: Optional[str] = os.getenv("CLUSTER_NAME")

    if not db_user or not db_password or not cluster_name:
        raise Exception("Please provide DB_USER, DB_PASSWORD, and CLUSTER_NAME in your .env file")

    db_name: Optional[str] = os.getenv("DB_NAME")
    if not db_name:
        raise Exception("Please provide DB_NAME in your .env file")

    uri: str = (
        f"mongodb+srv://{db_user}:{db_password}"
        f"@{cluster_name}.m7l3ilv.mongodb.net/{db_name}?retryWrites=true&w=majority"
    )

    try:
        me.connect(host=uri)
        logger.info("Connected to MongoDB!")
    except Exception as e:
        raise Exception(f"Unable to connect to MongoDB. Check your connection URI. {e}")


def setup_collection(collection_name: str) -> None:
    """Ensure the collection exists in the MongoDB database.

    Args:
        collection_name (str): Name of the collection to be created.
    """
    db = me.connection.get_db()
    if collection_name not in db.list_collection_names():
        logger.info(f"Creating collection: {collection_name}")
        db.create_collection(collection_name)
    else:
        logger.info(f"Collection {collection_name} already exists.")
