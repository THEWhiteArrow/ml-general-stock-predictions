import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from lib.logger.setup import setup_logger


logger = setup_logger(__name__)


def setup_mongodb() -> MongoClient:
    """A function that connects to MongoDB using the connection URI provided in the .env file.

    Raises:
        Exception: No DB_USER, DB_PASSWORD, or CLUSTER_NAME provided in the .env file
        Exception: Unable to connect to MongoDB. Check your connection URI.

    Returns:
        MongoClient: Client instance connected to MongoDB.
    """

    load_dotenv()

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    cluster_name = os.getenv("CLUSTER_NAME")

    if not db_user or not db_password or not cluster_name:
        raise Exception("Please provide DB_USER, DB_PASSWORD, and CLUSTER_NAME in your .env file")

    uri = f"mongodb+srv://{db_user}:{db_password}@{cluster_name}.m7l3ilv.mongodb.net/?retryWrites=true&w=majority&appName={cluster_name}"
    client = MongoClient(uri)

    try:
        client.admin.command("ping")
        logger.info("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        raise Exception(f"Unable to connect to MongoDB. Check your connection URI. {e}")

    return client


def setup_database(client: MongoClient) -> Database:
    """A function that sets up a database in MongoDB.

    Args:
        client (MongoClient): Client instance connected to MongoDB.

    Raises:
        Exception: Please provide DB_NAME in your .env file

    Returns:
        Database: Database instance in MongoDB.
    """

    load_dotenv()

    db_name = os.getenv("DB_NAME")

    if not db_name:
        raise Exception("Please provide DB_NAME in your .env file")

    if db_name not in client.list_database_names():
        logger.info(f"Creating database: {db_name}")

    return client[db_name]


def setup_collection(database: Database, collection_name: str) -> Collection:
    """A function that sets up a collection in MongoDB.

    Args:
        database (Database): Database instance in MongoDB.
        collection_name (str): Name of the collection to be created.

    Returns:
        Collection: Collection instance in MongoDB.
    """

    if collection_name not in database.list_collection_names():
        logger.info(f"Creating collection: {collection_name}")
        collection = database.create_collection(collection_name)
    else:
        collection = database.get_collection(collection_name)

    return collection
