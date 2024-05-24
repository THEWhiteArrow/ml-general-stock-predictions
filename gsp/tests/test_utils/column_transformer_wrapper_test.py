import pandas as pd
from gsp.utils.column_transformer_wrapper import ColumnTransformerWrapper
from sklearn.preprocessing import OneHotEncoder


def test_column_transformer_passes_through():
    # --- SETUP ---
    X = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
    ct = ColumnTransformerWrapper(
        transformers=[],
        remainder="passthrough",
    )

    # --- ACT ---
    result = ct.fit_transform(X)

    # --- ASSERT ---
    expected = pd.DataFrame({"remainder__a": [1, 2, 3], "remainder__b": [4, 5, 6], "remainder__c": [7, 8, 9]})
    print(result)
    print(expected)
    assert result.equals(expected)


def test_column_transformer_drops_remainder():
    # --- SETUP ---
    X = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
    ct = ColumnTransformerWrapper(
        transformers=[],
        remainder="drop",
    )

    # --- ACT ---
    result = ct.fit_transform(X)

    # --- ASSERT ---
    assert result.empty


def test_column_transformer_encodes_columns():
    # --- SETUP ---
    X = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    ct = ColumnTransformerWrapper(
        transformers=[
            ("encoder", OneHotEncoder(), ["b"]),
        ],
        remainder="passthrough",
    )

    # --- ACT ---
    result = ct.fit_transform(X)

    # --- ASSERT ---
    expected = pd.DataFrame(
        {
            "encoder__b_x": [1, 0, 0],
            "encoder__b_y": [0, 1, 0],
            "encoder__b_z": [0, 0, 1],
            "remainder__a": [1, 2, 3],
        }
    )
    result = result.astype(int)
    assert result.equals(expected)
