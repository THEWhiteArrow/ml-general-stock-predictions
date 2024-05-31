import re
from dataclasses import dataclass
import os
from typing import Dict, List, Optional
import pymongo as pm
from dotenv import load_dotenv
from lib.logger.setup import setup_logger
from generated.stock import Stock
from generated.generation import Generation
from gsp.mongodb.storage_collections import StorageCollections
from gsp.mongodb.stock_ref_mapping import StockRefMapping

logger = setup_logger(__name__)


@dataclass
class StorageHelper:
    client: Optional[pm.MongoClient] = None
    db_name: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    cluster_name: Optional[str] = None

    # --- GENERIC METHODS ---

    def setup_connection(self) -> "StorageHelper":
        logger.info("Setting up connection...")
        load_dotenv()

        db_user: Optional[str] = os.getenv("DB_USER")
        db_password: Optional[str] = os.getenv("DB_PASSWORD")
        cluster_name: Optional[str] = os.getenv("CLUSTER_NAME")
        db_name: Optional[str] = os.getenv("DB_NAME")

        if not db_user or not db_password or not cluster_name or not db_name:
            raise Exception("Please provide DB_USER, DB_PASSWORD, CLUSTER_NAME, and DB_NAME in your .env file")

        uri: str = (
            f"mongodb+srv://{db_user}:{db_password}"
            f"@{cluster_name}.m7l3ilv.mongodb.net/{db_name}?retryWrites=true&w=majority"
        )

        self.client = pm.MongoClient(uri)
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.cluster_name = cluster_name

        return self

    def close_connection(self) -> None:
        logger.info("Closing connection...")
        if self.client:
            self.client.close()  # type: ignore
            self.client = None

    def load_collection(self, collection_name: str, use_reference: bool = False):
        logger.info(f"Loading collection {collection_name}...")
        if self.client is None or self.db_name is None:
            raise Exception("No connection established")

        collection = self.client[self.db_name][collection_name]

        return collection

    def load_collection_documents(self, collection_name: str, reference: Dict[str, str] = {}):
        logger.info(f"Loading documents from {collection_name}...")
        collection = self.load_collection(collection_name)
        documents = list(collection.find())
        for document in documents:
            for field, ref_collection in reference.items():
                if field in document:
                    ref_ids = document[field] if isinstance(document[field], list) else [document[field]]
                    ref_data = list(self.load_collection(ref_collection).find({"_id": {"$in": ref_ids}}))
                    document[field] = ref_data if isinstance(document[field], list) else ref_data[0]
        return documents

    def insert_documents(self, collection_name: str, documents: List[Dict]):
        logger.info(f"Inserting documents into {collection_name}...")
        collection = self.load_collection(collection_name)
        results = collection.insert_many(documents)

        return results

    def delete_documents(self, collection_name: str, query: Dict) -> None:
        logger.info(f"Deleting documents from {collection_name}...")
        collection = self.load_collection(collection_name)
        collection.delete_many(query)

    # --- SPECIFIC METHODS ---
    # --- NOTE ---
    """
    The stocks should have a reference to both histories and generations.
    However, since the number of histories and generations can be extremely large and the stocks are relatively small,
    it is better to have the histories and generations reference the stocks instead.
    """

    def cleanse(self, pattern: str) -> None:
        logger.info("Cleansing database for storage helper...")
        if self.client is None or self.db_name is None:
            raise Exception("No connection established")

        for collection_name in StorageCollections:
            if re.search(pattern, collection_name.value):
                self.delete_documents(collection_name.value, {})

    def save_stocks(self, stocks: List[Stock]) -> pm.results.InsertManyResult:
        logger.info("Saving stocks...")
        stock_documents = [stock.to_dict() for stock in stocks]
        results = self.insert_documents(StorageCollections.STOCKS.value, stock_documents)

        return results

    def add_histories(self, mapping: StockRefMapping) -> pm.results.InsertManyResult:
        logger.info("Adding histories...")

        stocks_symbols: List[str] = mapping.get_symbols()
        stocks_collection: pm.collection.Collection = self.load_collection(StorageCollections.STOCKS.value)
        stocks_retrived: List[Dict] = list(stocks_collection.find({"symbol": {"$in": stocks_symbols}}))

        if len(stocks_retrived) != len(stocks_symbols):
            raise Exception("Some stocks are not found in the database")

        stocks_retrived_mapping: Dict[str, Dict] = {stock["symbol"]: stock for stock in stocks_retrived}

        all_histories: List[Dict] = []

        for stock_symbol, histories in mapping.get_items():
            all_histories.extend(
                [{**history.to_dict(), "stock": stocks_retrived_mapping[stock_symbol]["_id"]} for history in histories]
            )

        results = self.insert_documents(StorageCollections.HISTORIES.value, all_histories)

        return results

    def add_generation_with_predictions(
        self, generation: Generation, mapping: StockRefMapping
    ) -> pm.results.InsertManyResult:
        logger.info("Adding generation with predictions...")

        stocks_symbols: List[str] = mapping.get_symbols()
        stocks_collection: pm.collection.Collection = self.load_collection(StorageCollections.STOCKS.value)
        stocks_retrived: List[Dict] = list(stocks_collection.find({"symbol": {"$in": stocks_symbols}}))

        if len(stocks_retrived) != len(stocks_symbols):
            raise Exception("Some stocks are not found in the database")

        stocks_retrived_mapping: Dict[str, Dict] = {stock["symbol"]: stock for stock in stocks_retrived}

        generation_results = self.insert_documents(StorageCollections.GENERATIONS.value, [generation.to_dict()])
        generation_id: str = generation_results.inserted_ids[0]

        all_predictions: List[Dict] = []
        for stock_symbol, predictions in mapping.get_items():
            all_predictions.extend(
                [
                    {
                        **prediction.to_dict(),
                        "stock": stocks_retrived_mapping[stock_symbol]["_id"],
                        "generation": generation_id,
                    }
                    for prediction in predictions
                ]
            )

        predictions_results = self.insert_documents(StorageCollections.PREDICTIONS.value, all_predictions)

        return predictions_results
