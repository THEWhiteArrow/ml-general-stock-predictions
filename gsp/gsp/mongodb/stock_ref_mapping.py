from dataclasses import dataclass, field
import datetime
from typing import Dict, List, Optional, Tuple, TypeAlias, Union
from generated.history import History
from generated.prediction import Prediction

STOCK_NAME_ALIAS: TypeAlias = str


@dataclass
class StockRefMapping:

    mapping: Dict[STOCK_NAME_ALIAS, List[Union[History, Prediction]]] = field(default_factory=dict)

    def add(self, stock_name: STOCK_NAME_ALIAS, data: List[Union[History, Prediction]]) -> "StockRefMapping":
        if stock_name in self.mapping:
            self.mapping[stock_name].extend(data)
        else:
            self.mapping[stock_name] = data

        return self

    def get_by_symbol(self, stock_name: STOCK_NAME_ALIAS) -> List[Union[History, Prediction]]:
        return self.mapping.get(stock_name, [])

    def get_symbols(self) -> List[STOCK_NAME_ALIAS]:
        return list(self.mapping.keys())

    def get_items(self) -> List[Tuple[STOCK_NAME_ALIAS, List[Union[History, Prediction]]]]:
        return [(stock_name, stock) for stock_name, stock in self.mapping.items()]

    def filter_by_date(
        self, start_date: Optional[datetime.date], end_date: Optional[datetime.date]
    ) -> "StockRefMapping":

        start_date = start_date or datetime.date.min
        end_date = end_date or datetime.date.max

        start_date_obj = datetime.datetime.combine(start_date, datetime.datetime.min.time())
        end_date_obj = datetime.datetime.combine(end_date, datetime.datetime.max.time())

        for stock_name, data in self.mapping.items():
            self.mapping[stock_name] = [
                d for d in data if (d.date and d.date >= start_date_obj and d.date <= end_date_obj)
            ]

        return self
