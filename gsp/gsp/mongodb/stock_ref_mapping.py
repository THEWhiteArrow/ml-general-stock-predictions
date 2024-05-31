from dataclasses import dataclass, field
from typing import Dict, List, Tuple, TypeAlias, Union
from generated.history import History
from generated.prediction import Prediction

STOCK_NAME_ALIAS: TypeAlias = str


@dataclass
class StockRefMapping:

    mapping: Dict[STOCK_NAME_ALIAS, List[Union[History, Prediction]]] = field(default_factory=dict)

    def add_stock(self, stock_name: STOCK_NAME_ALIAS, data: List[Union[History, Prediction]]) -> "StockRefMapping":
        if stock_name in self.mapping:
            raise Exception(f"Stock name {stock_name} already exists in mapping")

        self.mapping[stock_name] = data

        return self

    def get_symbols(self) -> List[STOCK_NAME_ALIAS]:
        return list(self.mapping.keys())

    def get_items(self) -> List[Tuple[STOCK_NAME_ALIAS, List[Union[History, Prediction]]]]:
        return [(stock_name, stock) for stock_name, stock in self.mapping.items()]