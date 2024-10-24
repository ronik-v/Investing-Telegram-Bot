from abc import ABC, abstractmethod


class PortfolioFilter(ABC):
    def __init__(self, tickers_list, date_start, date_end):
        self.ticker_list = tickers_list
        self.date_start = date_start
        self.date_end = date_end

    @abstractmethod
    def filter(self) -> list[str]:
        raise NotImplemented


class Graph(ABC):
    def __init__(self, ticker, date_start, date_end, user_id):
        self.ticker = ticker
        self.date_start = date_start
        self.date_end = date_end
        self.user_id = user_id

    @abstractmethod
    def png_file_path(self) -> tuple[bytes, str]:
        raise NotImplemented
