import datetime
from lib.logger.setup import setup_logger
from gsp.model.model import generate_prediction
from gsp.publisher.run import run as publisher_run

logger = setup_logger(__name__)


def run(run_date: datetime.date):

    logger.info(f"Running GSP for {run_date.isoformat()}...")

    logger.info("Running Model...")
    generate_prediction(
        "Default multi-approach prediction",
        n_steps=15,
        days_back_to_consider=3 * 252,
        label_features=["year"],
        categorical_features=["day_of_week", "area_cat"],
        shift_list=[1, 2, 3],
        mwm_list=[5, 10, 15],
        single_problem_approach=False,
        hyper_params={},
    )
    logger.info("Publish results to database...")
    publisher_run(run_date)


if __name__ == "__main__":
    run_date = datetime.date.today()
    run(run_date=run_date)
