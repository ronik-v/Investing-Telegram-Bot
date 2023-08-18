from TickerDataParser import DataParser
from numpy import std
from abc import ABC, abstractmethod
from warnings import filterwarnings
filterwarnings('ignore')


#   Base model for creating filters
class PortfolioFilter(ABC):
    @abstractmethod
    def __init__(self, tickers_list, date_start, date_end):
        self.ticker_list = tickers_list
        self.date_start = date_start
        self.date_end = date_end

    @abstractmethod
    def filter(self) -> list[str]:
        pass


class BetaPositivePortfolioFilter(PortfolioFilter, ABC):
    def __init__(self, tickers_list, date_start, date_end):
        self.tickers_list = tickers_list
        self.date_start = date_start
        self.date_end = date_end
        self.beta = lambda df: round(float(df.cov()['SMA(5)'][1]) / float(df.std()['SMA(5)']), 3)
        self.tickers_price = DataParser.filter_parser(self.tickers_list, self.date_start, self.date_end)

    def filter(self) -> list[str]:
        tickers_filter_result = list()
        for key in self.tickers_price:
            if self.beta(self.tickers_price[key]) > 0:
                tickers_filter_result.append(key)
        return tickers_filter_result


class IncomeTickerFilter(PortfolioFilter, ABC):
    def __init__(self, tickers_list, date_start, date_end):
        self.tickers_list = tickers_list
        self.date_start = date_start
        self.date_end = date_end
        self.tickers_price = DataParser.filter_parser(self.tickers_list, self.date_start, self.date_end)

    def filter(self) -> list[str]:
        filter_result, pos = [], 0
        values = [sum(self.tickers_price[key]['DIFF']) for key in self.tickers_price.keys()]
        mean = sum(values) / len(values)
        for key in self.tickers_price.keys():
            if values[pos] > mean:
                filter_result.append(key)
            pos += 1
        return filter_result


class VolatilityTickerFilter(PortfolioFilter, ABC):
    def __init__(self, tickers_list, date_start, date_end):
        self.tickers_list = tickers_list
        self.date_start = date_start
        self.date_end = date_end
        self.tickers_price = DataParser.filter_parser(self.tickers_list, self.date_start, self.date_end)

    def filter(self) -> list[str]:
        filter_result, pos = [], 0
        values = [std(self.tickers_price[key]['SMA(5)']) for key in self.tickers_price.keys()]
        mean_std = sum(values) / len(values)
        for key in self.tickers_price.keys():
            if values[pos] < mean_std:
                filter_result.append(key)
            pos += 1
        return filter_result
