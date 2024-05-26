from typing import List, cast
from lib.logger.setup import setup_logger
from gsp.mongodb.models.generation import Generation
from gsp.mongodb.models.prediction import Prediction

logger = setup_logger(__name__)


def save_generation_predictions_to_mongodb(generation_doc: Generation, predictions_doc: List[Prediction]):

    existing_generation: Generation | None = cast(Generation | None, Generation.objects(prediction_date=generation_doc.prediction_date, name=generation_doc.name).first())  # type: ignore
    if existing_generation:
        logger.info(
            f"Generation {generation_doc.prediction_date} {generation_doc.name} already exists in MongoDb. Existing generation will be removed."
        )
        existing_generation.delete()

    try:
        logger.info(
            f"Saving Generation {generation_doc.prediction_date} {generation_doc.name} to MongoDB and associated predictions..."
        )
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
