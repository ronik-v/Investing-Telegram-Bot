import pandas_datareader as pdr
from pandas import DataFrame
from numpy import std
from sys import exit
from warnings import filterwarnings
filterwarnings('ignore')


class MakeBetaPositivePortfolio:
    def __init__(self, tickers_list, date_start, date_end):
        self.tickers_list = tickers_list
        self.date_start = date_start
        self.date_end = date_end
        self.beta = lambda df: round(float(df.cov()['SMA(5)'][1]) / float(df.std()['SMA(5)']), 3)
        self.tickers_dict_price = dict()
        self.tickers_list_result = list()

    def parsing_ticker(self, ticker, date_start, date_end) -> DataFrame:
        try:
            new_df = DataFrame(columns=['SMA(5)', 'STD', 'DIFF'])
            df_ticker = pdr.data.DataReader(ticker, 'moex', date_start, date_end)
            df_ticker['SMA(5)'] = df_ticker['CLOSE'].rolling(5).mean()
            df_ticker['STD'] = df_ticker['CLOSE'].rolling(5).std()
            df_ticker['DIFF'] = df_ticker['CLOSE'] - df_ticker['OPEN']
            new_df['SMA(5)'] = df_ticker['SMA(5)']
            new_df['STD'] = df_ticker['STD']
            new_df['DIFF'] = df_ticker['DIFF']
            return new_df
        except ImportError as Error:
            print(Error)
            exit(1)

    def parsing_tickers_list_price(self, tickers_list, date_start, date_end):
        for ticker in tickers_list:
            self.tickers_dict_price[ticker] = self.parsing_ticker(ticker, date_start, date_end)

    def BetaPositivePortfolio(self, tickers_list, date_start, date_end) -> list:
        self.parsing_tickers_list_price(tickers_list, date_start, date_end)
        for key in self.tickers_dict_price:
            if self.beta(self.tickers_dict_price[key]) > 0:
                self.tickers_list_result.append(key)
        return self.tickers_list_result


class IncomeTickerFilter(MakeBetaPositivePortfolio):
    def __init__(self, tickers_list, date_start, date_end):
        super().__init__(tickers_list, date_start, date_end)

    def income_filter(self) -> list:
        filter_result, pos = [], 0
        self.parsing_tickers_list_price(self.tickers_list, self.date_start, self.date_end)
        values = [sum(self.tickers_dict_price[key]['DIFF']) for key in self.tickers_dict_price.keys()]
        mean = sum(values) / len(values)
        for key in self.tickers_dict_price.keys():
            if values[pos] > mean:
                filter_result.append(key)
            pos += 1
        return filter_result


class VolatilityTickerFilter(MakeBetaPositivePortfolio):
    def __init__(self, tickers_list, date_start, date_end):
        super().__init__(tickers_list, date_start, date_end)

    def filter(self) -> list:
        filter_result, pos = [], 0
        self.parsing_tickers_list_price(self.tickers_list, self.date_start, self.date_end)
        values = [std(self.tickers_dict_price[key]['SMA(5)']) for key in self.tickers_dict_price.keys()]
        mean_std = sum(values) / len(values)
        for key in self.tickers_dict_price.keys():
            if values[pos] < mean_std:
                filter_result.append(key)
            pos += 1
        return filter_result
