from gsp.mongodb.transformation import transform_generation_predictions_to_mongodb_documents
import pandas as pd


def test_transform_generation_predictions_to_mongodb_documents_verifyies_all_columns():
    # --- SETUP ---
    generation_df = pd.DataFrame(
        {
            "PredictionDate": [pd.Period("2021-01-01")],
            "Name": ["AAPL"],
            "CreatedTimestamp": [pd.Timestamp.now()],
            "CategoricalFeatures": ["{}"],
            "LabelFeatures": ["{}"],
            "ShiftList": ["[1, 2, 3]"],
            "MWMList": ["[1, 2, 3]"],
            "DaysBackToConsider": [1],
            "NSteps": [1],
            "HyperParams": ["{}"],
        },
    )

    prediction_df = pd.DataFrame(
        {
            "Date": [pd.Period("2021-01-01")],
            "Name": ["AAPL"],
            "Close": [1.0],
        },
    )

    # --- ACT ---
    generation, predictions = transform_generation_predictions_to_mongodb_documents(
        generation_df=generation_df,
        prediction_df=prediction_df,
    )

    # --- ASSERT ---
    assert generation.prediction_date == "2021-01-01"
    assert generation.name == "AAPL"
    assert generation.created_timestamp == generation_df["CreatedTimestamp"][0]
    assert generation.categorical_features == {}
    assert generation.label_features == {}
    assert generation.shift_list == [1, 2, 3]
    assert generation.mwm_list == [1, 2, 3]
    assert generation.days_back_to_consider == 1
    assert generation.n_steps == 1
    assert generation.hyper_params == {}

    assert len(predictions) == 1
    assert predictions[0].date == "2021-01-01"
    assert predictions[0].name == "AAPL"
    assert predictions[0].close == 1.0


def test_transform_generation_predictions_to_mongodb_documents_raises_error_if_generation_df_is_empty():
    # --- SETUP ---
    generation_df = pd.DataFrame()

    prediction_df = pd.DataFrame(
        {
            "Date": [pd.Period("2021-01-01")],
            "Name": ["AAPL"],
            "Close": [1.0],
        },
    )

    # --- ACT ---
    try:
        transform_generation_predictions_to_mongodb_documents(
            generation_df=generation_df,
            prediction_df=prediction_df,
        )
    except ValueError as e:
        # --- ASSERT ---
        assert str(e) == "Generation dataframe is empty."


def test_transform_generation_predictions_to_mongodb_documents_raises_error_if_generation_df_does_not_contain_all_columns():
    # --- SETUP ---
    generation_df = pd.DataFrame(
        {
            "PredictionDate": [pd.Period("2021-01-01")],
            "Name": ["AAPL"],
            "CreatedTimestamp": [pd.Timestamp.now()],
            "CategoricalFeatures": ["{}"],
            "LabelFeatures": ["{}"],
            "ShiftList": ["[1, 2, 3]"],
            "MWMList": ["[1, 2, 3]"],
            "DaysBackToConsider": [1],
            "NSteps": [1],
        },
    )

    prediction_df = pd.DataFrame(
        {
            "Date": [pd.Period("2021-01-01")],
            "Name": ["AAPL"],
            "Close": [1.0],
        },
    )

    # --- ACT ---
    try:
        transform_generation_predictions_to_mongodb_documents(
            generation_df=generation_df,
            prediction_df=prediction_df,
        )
    except ValueError as e:
        # --- ASSERT ---
        assert str(e) == "Generation dataframe must contain the following columns: ['HyperParams']"
