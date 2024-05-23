import pandas as pd
from typing import Dict, List, Tuple
from lib.logger.setup import setup_logger

logger = setup_logger(__name__)


def transform_generation_predictions_to_mongodb_documents(
    generation_df: pd.DataFrame, prediction_df: pd.DataFrame
) -> Tuple[List[Dict], List[Dict]]:
    """A function that transforms dataframes into MongoDB documents.

    Args:
        generation_df (pd.DataFrame): Dataframe containing generation data.
        prediction_df (pd.DataFrame): Dataframe containing prediction data.
    """
    logger.info("Transforming dataframes into mongodb documents...")
    generations_doc = generation_df.to_dict(orient="records")
    predictions_doc = prediction_df.to_dict(orient="records")

    return generations_doc, predictions_doc
