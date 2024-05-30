from dataclasses import dataclass
import os
from typing import Dict, List, Literal, Optional, Tuple
import pymongo as pm
from dotenv import load_dotenv
from lib.logger.setup import setup_logger
from generated.stock import Stock, History, Prediction
from gsp.mongodb.storage_collections import StorageCollections

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
            self.client.close()
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

    def delete_stocks(self, cascade: bool = True) -> None:
        logger.info("Deleting stocks...")
        self.delete_documents(StorageCollections.STOCKS.value, {})
        if cascade:
            self.delete_documents(StorageCollections.HISTORIES.value, {})
            self.delete_documents(StorageCollections.PREDICTIONS.value, {})

    def save_stocks(self, stocks: List[Stock]):
        """An optimized method to save stocks, histories, and predictions in one go.

        Args:
            stocks (List[Stock]): List of Stock objects

        Returns:
            InsertManyResult: Resutls of the insert_many operation
        """
        logger.info("Saving stocks...")

        stocks_history_mapping: List[Tuple[str, int]] = []
        stocks_prediction_mapping: List[Tuple[str, int]] = []
        all_histories: List[History] = []
        all_predictions: List[Prediction] = []
        all_stocks_dicts: List[Dict] = []

        stocks_history_mapping = [(stock.symbol, len(stock.histories)) for stock in stocks]
        stocks_prediction_mapping = [(stock.symbol, len(stock.predictions)) for stock in stocks]
        all_histories = [history for stock in stocks for history in stock.histories]
        all_predictions = [prediction for stock in stocks for prediction in stock.predictions]

        if all_histories:
            histories_res = self.save_histories(all_histories)
        else:
            histories_res = None

        if all_predictions:
            predictions_res = self.save_predictions(all_predictions)
        else:
            predictions_res = None

        history_counter = 0
        prediction_counter = 0

        for i, stock in enumerate(stocks):
            stock_dict = stock.to_dict()

            if histories_res is not None:
                stock_dict["histories"] = histories_res.inserted_ids[
                    history_counter : history_counter + stocks_history_mapping[i][1]
                ]

            if predictions_res is not None:
                stock_dict["predictions"] = predictions_res.inserted_ids[
                    prediction_counter : prediction_counter + stocks_prediction_mapping[i][1]
                ]

            all_stocks_dicts.append(stock_dict)
            history_counter += stocks_history_mapping[i][1]
            prediction_counter += stocks_prediction_mapping[i][1]

        stocks_res = self.insert_documents(StorageCollections.STOCKS.value, all_stocks_dicts)
        return stocks_res

    def save_histories(self, histories: List[History]):
        logger.info("Saving histories...")
        histories_dicts = [history.to_dict() for history in histories]
        histories_res = self.insert_documents(StorageCollections.HISTORIES.value, histories_dicts)

        return histories_res

    def save_predictions(self, predictions: List[Prediction]):
        logger.info("Saving predictions...")
        predictions_dicts = [prediction.to_dict() for prediction in predictions]
        predictions_res = self.insert_documents(StorageCollections.PREDICTIONS.value, predictions_dicts)

        return predictions_res

    def find_stock(self, symbol: str) -> Optional[Stock]:
        logger.info(f"Finding stock with symbol {symbol}...")
        collection = self.load_collection(StorageCollections.STOCKS.value)
        stock = collection.find_one({"symbol": symbol})
        if stock is None:
            return None

        stock["histories"] = list(
            self.load_collection(StorageCollections.HISTORIES.value).find({"_id": {"$in": stock["histories"]}})
        )

        stock["predictions"] = list(
            self.load_collection(StorageCollections.PREDICTIONS.value).find({"_id": {"$in": stock["predictions"]}})
        )

        return Stock.from_dict(stock)

    def add_predictions_to_stocks(self, mapping: Dict[str, List[Prediction]]):
        logger.info("Adding predictions to stocks...")

        stocks_prediction_mapping: List[Tuple[str, int]] = []
        all_predictions: List[Prediction] = []

        stocks_prediction_mapping = [(symbol, len(predictions)) for symbol, predictions in mapping.items()]
        all_predictions = [prediction for predictions in mapping.values() for prediction in predictions]

        predictions_res = self.save_predictions(all_predictions)

        prediction_counter = 0
        all_stocks_dicts: List[Dict] = []

        for symbol, count in stocks_prediction_mapping:
            stock = self.find_stock(symbol)
            if stock is None:
                logger.warning(f"Stock with symbol {symbol} not found")
                raise Exception(f"Stock with symbol {symbol} not found")

            stock_dict = stock.to_dict()
            stock_dict["predictions"] = predictions_res.inserted_ids[prediction_counter : prediction_counter + count]
            all_stocks_dicts.append(stock_dict)

            prediction_counter += count

        raise NotImplementedError("This method is not implemented yet")
        # stocks_res = self.insert_documents(StorageCollections.STOCKS.value, all_stocks_dicts)
        # return stocks_res
