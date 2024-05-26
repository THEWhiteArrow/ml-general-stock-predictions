from dataclasses import dataclass
from typing import Any, List, Literal, Tuple, cast
import pandas as pd
from sklearn.compose import ColumnTransformer


@dataclass
class ColumnTransformerWrapper:
    """A class that wraps the ColumnTransformer from sklearn.compose.
    It transforms the pandas DataFrame and returns the transformed DataFrame.

    NOTE: The wrapper will change the names of the columns after transformation.
    """

    transformers: List[Tuple[str, Any, List[str]]]
    remainder: Literal["drop", "passthrough"] = "passthrough"
    allow_column_prefix: bool = True

    def fit_transform(self, X: pd.DataFrame, y: Any | None = None) -> pd.DataFrame:  # type: ignore
        ct = ColumnTransformer(self.transformers, remainder=self.remainder)

        transformed_X = ct.fit_transform(X, y)
        columns = cast(List[str], ct.get_feature_names_out())

        if not self.allow_column_prefix:
            columns = [column.split("__")[-1] for column in columns]

        return pd.DataFrame(
            transformed_X,  # type: ignore
            index=X.index,
            columns=columns,
        )
