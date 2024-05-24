from dataclasses import dataclass
from typing import Any, List, Literal, Tuple
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

    def fit_transform(self, X: pd.DataFrame, y: Any | None = None) -> pd.DataFrame:  # type: ignore
        ct = ColumnTransformer(self.transformers, remainder=self.remainder)

        return pd.DataFrame(
            ct.fit_transform(X, y),  # type: ignore
            index=X.index,
            columns=ct.get_feature_names_out(),
        )
