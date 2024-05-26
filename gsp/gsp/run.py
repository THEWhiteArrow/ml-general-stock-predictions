from lib.logger.setup import setup_logger
from gsp.scraper.run import scrape
from gsp.algorithms.model import generate_prediction
from gsp.mongodb.run import publish

logger = setup_logger(__name__)


def run():
    logger.info("Running GSP...")

    logger.info("Running Scraper...")
    scrape()

    logger.info("Running Model...")
    prediction_date = generate_prediction(
        "Default multi-approach prediction",
        n_steps=15,
        days_back_to_consider=3 * 252,
        label_features=["Year"],
        categorical_features=["DayOfWeek", "AreaCat"],
        shift_list=[1, 2, 3],
        mwm_list=[5, 10, 15],
        single_problem_approach=False,
        hyper_params={},
    )

    logger.info("Running Publish...")
    publish(prediction_date=prediction_date)


if __name__ == "__main__":
    run()
