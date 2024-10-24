from typing import override
from numpy import std
from pandas import DataFrame
from warnings import filterwarnings

from ticker_data_parser import DataParser

from abstract import PortfolioFilter

filterwarnings('ignore')


class BetaPositivePortfolioFilter(PortfolioFilter):
    def __init__(self, tickers_list, date_start, date_end):
        super().__init__(tickers_list, date_start, date_end)

        self.beta = lambda df: round(float(df.cov()['SMA(5)'][1]) / float(df.std()['SMA(5)']), 3)
        self.tickers_price: dict[str, DataFrame] = DataParser.filter_parser(tickers_list, date_start, date_end)

    @override
    def filter(self) -> list[str]:
        tickers_filter_result = list()
        for key in self.tickers_price:
            if self.beta(self.tickers_price[key]) > 0:
                tickers_filter_result.append(key)
        return tickers_filter_result


class IncomeTickerFilter(PortfolioFilter):
    def __init__(self, tickers_list, date_start, date_end):
        super().__init__(tickers_list, date_start, date_end)

        self.tickers_price: dict[str, DataFrame] = DataParser.filter_parser(tickers_list, date_start, date_end)

    @override
    def filter(self) -> list[str]:
        filter_result, pos = [], 0
        values = [sum(self.tickers_price[key]['DIFF']) for key in self.tickers_price.keys()]
        mean = sum(values) / len(values)
        for key in self.tickers_price.keys():
            if values[pos] > mean:
                filter_result.append(key)
            pos += 1
        return filter_result


class VolatilityTickerFilter(PortfolioFilter):
    def __init__(self, tickers_list, date_start, date_end):
        super().__init__(tickers_list, date_start, date_end)

        self.tickers_price: dict[str, DataFrame] = DataParser.filter_parser(tickers_list, date_start, date_end)

    @override
    def filter(self) -> list[str]:
        filter_result, pos = [], 0
        values = [std(self.tickers_price[key]['SMA(5)']) for key in self.tickers_price.keys()]
        mean_std = sum(values) / len(values)
        for key in self.tickers_price.keys():
            if values[pos] < mean_std:
                filter_result.append(key)
            pos += 1
        return filter_result
