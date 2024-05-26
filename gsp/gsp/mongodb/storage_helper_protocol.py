from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Union
from gsp.mongodb.models.prediction import Prediction
from gsp.mongodb.models.history import History
from gsp.mongodb.models.generation import Generation
from injector import inject
import pandas as pd


@inject
@dataclass
class StorageHelperProtocol(ABC):

    @abstractmethod
    def setup_connection(self) -> "StorageHelperProtocol":
        pass

    @abstractmethod
    def save_generation(self, data: Union[List[Generation], Generation]) -> List[Generation]:
        pass

    @abstractmethod
    def save_prediction(self, data: Union[List[Prediction], Prediction]) -> List[Prediction]:
        pass

    @abstractmethod
    def save_history(self, data: Union[List[History], History]) -> List[History]:
        pass

    @abstractmethod
    def load_history(self) -> pd.DataFrame:
        pass
