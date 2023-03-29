from pandas import DataFrame
import pandas_datareader as pdr


class DataParser:
    def __init__(self, tickers: list, date_start: str, date_end: str):
        self.tickers = tickers
        self.date_start = date_start
        self.date_end = date_end
        self.DF_tickers = DataFrame(columns=tickers)

    def parse_ticker_for_dynamics(self, ticker) -> DataFrame:
        df = pdr.data.DataReader(ticker, 'moex', self.date_start, self.date_end)['CLOSE']
        df['SMA5'] = df['CLOSE'].rolling(5).mean()
        df['SMA12'] = df['CLOSE'].rolling(12).mean()
        df['EWMA'] = df['CLOSE'].ewm(com=5).mean()
        return df

    def parse_df_ticker(self, ticker):
        close_prices = []
        df = pdr.data.DataReader(ticker, 'moex', self.date_start, self.date_end)['CLOSE']
        for price in df:
            close_prices.append(price)
        return close_prices

    def parse_tickers(self) -> DataFrame:
        for ticker in self.tickers:
            self.DF_tickers[ticker] = self.parse_df_ticker(ticker)
        return self.DF_tickers
