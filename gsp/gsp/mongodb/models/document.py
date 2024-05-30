from dataclasses import dataclass, asdict
import pandas as pd


@dataclass
class Document:

    def copy(self):
        return self.__class__(**self.__dict__)

    def to_dict(self):
        return asdict(self)

    def to_dataframe(self):
        return pd.DataFrame([self.to_dict()])

    def from_dict(self, data):
        return self.__class__(**data)

    def from_dataframe(self, df: pd.DataFrame):
        return self.from_dict(df.to_dict(orient="records")[0])
