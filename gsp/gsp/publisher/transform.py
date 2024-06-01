from typing import List
import pandas as pd
from generated.generation import Generation
from generated.history import History
from generated.prediction import Prediction
from generated.stock import Stock


def transform_to_generation(df: pd.DataFrame) -> Generation:
    generation_data = df.head(1).to_dict(orient="records")[0]
    generation = Generation.from_dict(generation_data)
    return generation


def transform_to_predictions(df: pd.DataFrame) -> List[Prediction]:
    prediction_data = df.to_dict(orient="records")
    predictions = [Prediction.from_dict(prediction) for prediction in prediction_data]
    return predictions


def transform_to_stocks(df: pd.DataFrame) -> List[Stock]:
    stocks_data = df.to_dict(orient="records")
    stocks = [Stock.from_dict(stock) for stock in stocks_data]
    return stocks


def transform_to_histories(df: pd.DataFrame) -> List[History]:
    histories = [History.from_dict(stock) for stock in df.to_dict(orient="records")]
    return histories
