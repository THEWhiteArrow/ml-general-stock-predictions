import os
from typing import List, Optional, Union, cast
from dotenv import load_dotenv
import mongoengine as me
from pymongo import MongoClient
import pandas as pd
from gsp.mongodb.models.generation import Generation
from gsp.mongodb.models.history import History
from gsp.mongodb.models.prediction import Prediction
from gsp.mongodb.storage_helper_protocol import StorageHelperProtocol
from injector import inject
from dataclasses import dataclass


@inject
@dataclass
class StorageHelper(StorageHelperProtocol):
    mongo_client: Union[None, MongoClient] = None

    def setup_connection(self) -> "StorageHelperProtocol":
        load_dotenv()

        db_user: Optional[str] = os.getenv("DB_USER")
        db_password: Optional[str] = os.getenv("DB_PASSWORD")
        cluster_name: Optional[str] = os.getenv("CLUSTER_NAME")
        db_name: Optional[str] = os.getenv("DB_NAME")

        if not db_user or not db_password or not cluster_name or not db_name:
            raise Exception("Not all required environment variables are set. Please check your .env file.")

        uri: str = (
            f"mongodb+srv://{db_user}:{db_password}"
            f"@{cluster_name}.m7l3ilv.mongodb.net/{db_name}?retryWrites=true&w=majority"
        )

        try:
            self.mongo_client = me.connect(host=uri)
        except Exception as e:
            raise Exception(f"Unable to connect to MongoDB. Check your connection URI. {e}")

        return self

    def save_generation(self, data: Union[List[Generation], Generation]) -> List[Generation]:
        if not self.mongo_client:
            raise Exception("MongoDB connection not set up. Call setup_connection() first.")
        if Generation._get_collection_name() is None:
            raise Exception("Collection name not set. Please set the collection name in the Generation class.")
        if isinstance(data, Generation):
            data = cast(List[Generation], [data])

        for generation in data:
            existing_generation = cast(
                Union[Generation, None],
                Generation.objects(  # type: ignore
                    prediction_date=generation.prediction_date, name=generation.name
                ).first(),
            )

            if existing_generation is not None:
                existing_generation.delete()

        saved_data = cast(List[Generation], Generation.objects.insert(data))  # type: ignore
        return saved_data

    def save_prediction(self, data: Union[List[Prediction], Prediction]) -> List[Prediction]:
        if not self.mongo_client:
            raise Exception("MongoDB connection not set up. Call setup_connection() first.")
        if Prediction._get_collection_name() is None:
            raise Exception("Collection name not set. Please set the collection name in the Prediction class.")
        if isinstance(data, Prediction):
            data = cast(List[Prediction], [data])

        saved_data = cast(List[Prediction], Prediction.objects.insert(data))  # type: ignore
        return saved_data

    def save_history(self, data: Union[List[History], History]) -> List[History]:
        if not self.mongo_client:
            raise Exception("MongoDB connection not set up. Call setup_connection() first.")
        if History._get_collection_name() is None:
            raise Exception("Collection name not set. Please set the collection name in the History class.")
        if isinstance(data, History):
            data = cast(List[History], [data])

        saved_data = cast(List[History], History.objects.insert(data))  # type: ignore
        return saved_data

    def load_history(self) -> pd.DataFrame:
        all_history: List[History] = History.objects().all()  # type: ignore

        if not all_history:
            return pd.DataFrame()

        return pd.DataFrame(
            [
                {
                    "Date": history.date,
                    "Name": history.name,
                    "Close": history.close,
                    "Volume": history.volume,
                    "Open": history.open,
                    "High": history.high,
                    "Low": history.low,
                }
                for history in all_history
            ],
        )
