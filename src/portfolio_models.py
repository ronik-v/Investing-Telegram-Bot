from pandas import DataFrame
from ticker_data_parser import DataParser
import numpy as np


class MarkovModel:
    def __init__(self, tickers: list[str], date_start: str, date_end: str, portfolio_cost: int):
        self.tickers = tickers
        self.date_start = date_start
        self.date_end = date_end
        self.df_close = DataParser(tickers, date_start, date_end).parse_tickers()
        self.portfolio_cost = portfolio_cost
        self.df_close_data = self.df_close.pct_change()
        self.df_close_mean = self.df_close_data.mean()
        self.cov_matrix = self.df_close_data.cov()
        self.tickers_amount = len(self.df_close.columns)

    def random_portfolio(self):
        result = np.exp(np.random.randn(self.tickers_amount))
        result = result / result.sum()
        return result

    def profitability_of_portfolio(self, random_port):
        return np.matmul(self.df_close_mean.values, random_port)

    def risk_of_portfolio(self, random_port):
        return np.sqrt(np.matmul(np.matmul(random_port, self.cov_matrix.values), random_port))

    def get_last_prices(self) -> list:
        last_prices = list()
        for ticker in self.df_close.columns:
            last_prices.append(self.df_close[ticker][len(self.df_close) - 1])
        return last_prices

    def create_portfolio_df(self, weights):
        portfolio_df = DataFrame([weights * 100], columns=self.df_close.columns, index=['доли, %']).T
        portfolio_df['Цена сейчас'] = self.get_last_prices()
        portfolio_df['Количество акций'] = ((portfolio_df['доли, %'] / 100) * self.portfolio_cost) / portfolio_df['Цена сейчас']
        portfolio_df['Количество акций'] = portfolio_df['Количество акций'].round(0)
        return portfolio_df.round(2)[['доли, %', 'Цена сейчас', 'Количество акций']]

    def result(self, iterations=800) -> list[str]:
        portfolio_structure = []
        risk = np.zeros(iterations)
        doh = np.zeros(iterations)
        portf = np.zeros((iterations, self.tickers_amount))

        for it in range(iterations):
            r = self.random_portfolio()
            portf[it, :] = r
            risk[it] = self.risk_of_portfolio(r)
            doh[it] = self.profitability_of_portfolio(r)

        min_risk = np.argmin(risk)
        max_sharp_coefficient = np.argmax(doh / risk)

        r_mean = np.ones(self.tickers_amount) / self.tickers_amount
        risk_mean = self.risk_of_portfolio(r_mean)

        minimal_risk = self.create_portfolio_df(portf[min_risk])
        maximum_sharpe_ratio = self.create_portfolio_df(portf[max_sharp_coefficient])
        medium_portfolio = self.create_portfolio_df(r_mean)

        portfolio_structure.append('Минимальный риск\n')
        portfolio_structure.append("риск = %1.2f%%" % (float(risk[min_risk]) * 100.))
        portfolio_structure.append(minimal_risk)
        portfolio_structure.append('\nМаксимальный коэффициент Шарпа\n')
        portfolio_structure.append("риск = %1.2f%%" % (float(risk[max_sharp_coefficient]) * 100.))
        portfolio_structure.append(maximum_sharpe_ratio)
        portfolio_structure.append('\nСредний портфель\n')
        portfolio_structure.append("риск = %1.2f%%" % (float(risk_mean) * 100.))
        portfolio_structure.append(medium_portfolio)
        return portfolio_structure
