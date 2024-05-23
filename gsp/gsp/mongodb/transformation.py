import json
from gsp.mongodb.models.generation import Generation
from gsp.mongodb.models.prediction import Prediction
import pandas as pd
from typing import List, Tuple, cast
from lib.logger.setup import setup_logger

logger = setup_logger(__name__)


def transform_generation_predictions_to_mongodb_documents(
    generation_df: pd.DataFrame, prediction_df: pd.DataFrame
) -> Tuple[Generation, List[Prediction]]:
    """A function that transforms dataframes into MongoDB documents.

    Args:
        generation_df (pd.DataFrame): Dataframe containing generation data.
        prediction_df (pd.DataFrame): Dataframe containing prediction data.
    """
    logger.info("Transforming dataframes into mongodb documents...")

    if generation_df.empty:
        raise ValueError("Generation dataframe is empty.")

    if prediction_df.empty:
        raise ValueError("Prediction dataframe is empty.")

    predictions_doc: List[Prediction] = [
        Prediction(
            date=cast(pd.Period, row["Date"]).to_timestamp().date().isoformat(),
            name=row["Name"],
            close=row["Close"],
        )
        for row in prediction_df.to_dict(orient="records")
    ]
    generation_row = generation_df.iloc[0]
    generation_doc: Generation = Generation(
        prediction_date=cast(pd.Period, generation_row["PredictionDate"]).to_timestamp().date().isoformat(),
        name=generation_row["Name"],
        created_timestamp=generation_row["CreatedTimestamp"],
        categorical_features=json.loads(generation_row["CategoricalFeatures"]),
        label_features=json.loads(generation_row["LabelFeatures"]),
        shift_list=json.loads(generation_row["ShiftList"]),
        mwm_list=json.loads(generation_row["MWMList"]),
        days_back_to_consider=generation_row["DaysBackToConsider"],
        n_steps=generation_row["NSteps"],
        hyper_params=json.loads(generation_row["HyperParams"]),
        predictions=[],
    )

    return generation_doc, predictions_doc
