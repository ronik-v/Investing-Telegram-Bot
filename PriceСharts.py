import pandas_datareader as pdr
import matplotlib.pyplot as plt


class TickerDynamics:
    def __init__(self, ticker, date_start, date_end, user_id):
        self.ticker = ticker
        self.date_start = date_start
        self.date_end = date_end
        self.user_id = user_id
        self.df = pdr.data.DataReader(ticker, 'moex', date_start, date_end)
        self.df['SMA5'] = self.df['CLOSE'].rolling(5).mean()
        self.df['SMA12'] = self.df['CLOSE'].rolling(12).mean()
        self.df['EWMA'] = self.df['CLOSE'].ewm(com=5).mean()

    def dynamics_graph(self) -> str:
        fig = plt.figure(figsize=(10, 8))
        plt.plot(self.df['CLOSE'], label=f'Close price {self.ticker}')
        plt.plot(self.df['SMA5'], label='SMA(5)')
        plt.plot(self.df['SMA12'], label='SMA(12)')
        plt.plot(self.df['EWMA'], label='EWMA')
        plt.title(f'{self.ticker} c {self.date_start} по {self.date_end}')
        plt.xlabel('Дата')
        plt.ylabel('RUB')
        plt.legend()
        plt.grid(True)
        fig.savefig(f"{self.user_id}_ma.png")
        return f"{self.user_id}_ma.png"


class JapaneseCandlesDynamics:
    def __init__(self, ticker, date_start, date_end, user_id):
        self.ticker = ticker
        self.date_start = date_start
        self.date_end = date_end
        self.user_id = user_id
        self.prices = pdr.data.DataReader(ticker, 'moex', date_start, date_end)

    def candles_graph(self):
        fig = plt.figure(figsize=(10, 8))
        width = .8
        width2 = .09
        up = self.prices[self.prices.CLOSE >= self.prices.OPEN]
        down = self.prices[self.prices.CLOSE < self.prices.OPEN]
        col1 = 'green'
        col2 = 'red'
        plt.bar(up.index, up.CLOSE - up.OPEN, width, bottom=up.OPEN, color=col1)
        plt.bar(up.index, up.HIGH - up.CLOSE, width2, bottom=up.CLOSE, color=col1)
        plt.bar(up.index, up.LOW - up.OPEN, width2, bottom=up.OPEN, color=col1)
        plt.bar(down.index, down.CLOSE - down.OPEN, width, bottom=down.OPEN, color=col2)
        plt.bar(down.index, down.HIGH - down.OPEN, width2, bottom=down.OPEN, color=col2)
        plt.bar(down.index, down.LOW - down.CLOSE, width2, bottom=down.CLOSE, color=col2)
        plt.title(f'{self.ticker} c {self.date_start} по {self.date_end}')
        plt.xlabel('Дата')
        plt.ylabel('RUB')
        plt.grid(True)
        plt.xticks(rotation=45, ha='right')
        fig.savefig(f"{self.user_id}_candles.png")
        return f"{self.user_id}_candles.png"
