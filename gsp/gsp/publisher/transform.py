import json
import pandas as pd
from generated.generation import Generation
from typing import List, cast
from generated.history import History
from generated.prediction import Prediction
from generated.stock import Stock
from gsp.mongodb.stock_ref_mapping import StockRefMapping
from lib.logger.setup import setup_logger

logger = setup_logger(__name__)


def transform_generation(df: pd.DataFrame) -> Generation:
    logger.info("Transforming generation data...")
    columns_to_json_load = ["categorical_features", "label_features", "shifts", "mwms", "hyper_params"]
    for column in columns_to_json_load:
        df[column] = df[column].apply(json.loads)

    generation_data = df.head(1).to_dict(orient="records")[0]

    generation = Generation.from_dict(
        {
            "date": generation_data["date"],
            "name": generation_data["name"],
            "created_at": generation_data["created_at"],
            "categorical_features": generation_data["categorical_features"],
            "label_features": generation_data["label_features"],
            "shifts": generation_data["shifts"],
            "mwms": generation_data["mwms"],
            "days_back_to_consider": generation_data["days_back_to_consider"],
            "hyper_params": generation_data["hyper_params"],
            "n_step": generation_data["n_step"],
        }
    )
    return generation


def transform_stocks(df: pd.DataFrame) -> List[Stock]:
    logger.info("Transforming stocks data...")
    stocks_symbols = df["symbol"].unique()
    stocks: List[Stock] = []

    for stock_symbol in stocks_symbols:
        stock_df = cast(pd.DataFrame, df[df["symbol"] == stock_symbol])
        stock_data = stock_df.head(1).to_dict(orient="records")[0]
        stock = Stock.from_dict(stock_data)
        stocks.append(stock)

    return stocks


def transform_predictions(df: pd.DataFrame) -> StockRefMapping:
    logger.info("Transforming predictions data...")
    mapping = StockRefMapping()
    stock_symbols = df["symbol"].unique()

    for stock_symbol in stock_symbols:
        stock_df = df.where(df["symbol"] == stock_symbol).dropna()
        predictions_data = stock_df.to_dict(orient="records")
        predictions = [Prediction.from_dict(prediction) for prediction in predictions_data]
        mapping.add(stock_symbol, predictions)  # type: ignore

    return mapping


def transform_histories(df: pd.DataFrame) -> StockRefMapping:
    logger.info("Transforming histories data...")
    mapping = StockRefMapping()
    stock_symbols = df["symbol"].unique()

    for stock_symbol in stock_symbols:
        stock_df = cast(pd.DataFrame, df[df["symbol"] == stock_symbol])
        histories_data = stock_df.to_dict(orient="records")
        histories = [History.from_dict(history) for history in histories_data]
        mapping.add(stock_symbol, histories)  # type: ignore

    return mapping
