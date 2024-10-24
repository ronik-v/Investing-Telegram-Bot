import requests
from pandas import DataFrame


class DataParser:
    def __init__(self, tickers: list, date_start: str, date_end: str):
        self.tickers = tickers
        self.date_start = date_start
        self.date_end = date_end
        self.DF_tickers = DataFrame(columns=tickers)

    @staticmethod
    def get_base_df(ticker: str, date_start: str, date_end: str) -> DataFrame:
        url = f"https://iss.moex.com/iss/history/engines/stock/markets/shares/securities/{ticker}.json"
        params = {
            'from': date_start,
            'till': date_end
        }
        response = requests.get(url, params=params)
        data = response.json()['history']['data']

        if not data:
            print(f"Нет данных для тикера {ticker} в указанный период.")
            return DataFrame(columns=['CLOSE', 'OPEN'])  # Возвращаем пустой DataFrame с нужными колонками

        columns = response.json()['history']['columns']
        df = DataFrame(data, columns=columns)
        return df

    @classmethod
    def filter_parser(cls, tickers_list: list[str], date_start: str, date_end: str) -> dict[str, DataFrame]:
        tickers_prices = dict()
        for ticker in tickers_list:
            new_df = DataFrame(columns=['SMA(5)', 'STD', 'DIFF'])
            df_ticker = cls.get_base_df(ticker, date_start, date_end)
            df_ticker['CLOSE'] = df_ticker['CLOSE'].astype(float)
            df_ticker['SMA(5)'] = df_ticker['CLOSE'].rolling(5).mean()
            df_ticker['STD'] = df_ticker['CLOSE'].rolling(5).std()
            df_ticker['DIFF'] = df_ticker['CLOSE'] - df_ticker['OPEN'].astype(float)
            new_df['SMA(5)'] = df_ticker['SMA(5)']
            new_df['STD'] = df_ticker['STD']
            new_df['DIFF'] = df_ticker['DIFF']
            tickers_prices[ticker] = new_df
        return tickers_prices

    def parse_ticker_for_dynamics(self, ticker) -> DataFrame:
        df = self.get_base_df(ticker, self.date_start, self.date_end)
        df['CLOSE'] = df['CLOSE'].astype(float)
        df['SMA5'] = df['CLOSE'].rolling(5).mean()
        df['SMA12'] = df['CLOSE'].rolling(12).mean()
        df['EWMA'] = df['CLOSE'].ewm(com=5).mean()
        return df

    def parse_df_ticker(self, ticker):
        close_prices = []
        df = self.get_base_df(ticker, self.date_start, self.date_end)
        df['CLOSE'] = df['CLOSE'].astype(float)

        for price in df['CLOSE']:
            close_prices.append(price)

        return close_prices

    def parse_tickers(self) -> DataFrame:
        all_close_prices = []

        for ticker in self.tickers:
            close_prices = self.parse_df_ticker(ticker)
            all_close_prices.append(close_prices)

        min_length = min(len(prices) for prices in all_close_prices)

        for i, ticker in enumerate(self.tickers):
            self.DF_tickers[ticker] = all_close_prices[i][:min_length]

        return self.DF_tickers

