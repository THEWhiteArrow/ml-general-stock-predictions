from typing import List
from lib.logger.setup import setup_logger
from gsp.mongodb.models.generation import Generation
from gsp.mongodb.models.prediction import Prediction

logger = setup_logger(__name__)


def save_generation_predictions_to_mongodb(generation_doc: Generation, predictions_doc: List[Prediction]):
    # TODO: Overwrite the existing predictions if the generation already exists

    try:
        # --- PREDICTION ---
        Prediction.objects.insert(predictions_doc)  # type: ignore

        # --- UPDATE REFERENCE ---
        generation_doc.predictions.extend(prediction.id for prediction in predictions_doc)  # type: ignore

        # --- GENERATION ---
        generation_doc.save()

    except Exception as e:
        logger.error(f"Unable to save data to MongoDB. Removing all added instances in the transation. {e}")
        for prediction in predictions_doc:
            if prediction.id:  # type: ignore
                prediction.delete()

        if generation_doc.id:  # type: ignore
            generation_doc.delete()
        raise Exception(f"Unable to save data to MongoDB. {e}")
