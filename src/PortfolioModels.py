from pandas import DataFrame
from TickerDataParser import DataParser
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

    def result(self) -> list[str]:
        iterations = 800
        portfolio_structure = list()
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

        minimal_risk = DataFrame([portf[min_risk] * 100], columns=self.df_close.columns, index=['доли, %']).T
        minimal_risk['Цена сейчас'] = self.get_last_prices()
        minimal_risk['Количество акций'] = ((minimal_risk['доли, %'] / 100) * self.portfolio_cost) / minimal_risk['Цена сейчас']
        minimal_risk['Количество акций'] = minimal_risk['Количество акций'].round(0)
        minimal_risk = minimal_risk.round(2)
        del minimal_risk[minimal_risk.columns[1]]

        maximum_sharpe_ratio = DataFrame([portf[max_sharp_coefficient] * 100], columns=self.df_close.columns, index=['доли, %']).T
        maximum_sharpe_ratio['Цена сейчас'] = self.get_last_prices()
        maximum_sharpe_ratio['Количество акций'] = ((maximum_sharpe_ratio['доли, %'] / 100) * self.portfolio_cost) / maximum_sharpe_ratio['Цена сейчас']
        maximum_sharpe_ratio['Количество акций'] = maximum_sharpe_ratio['Количество акций'].round(0)
        maximum_sharpe_ratio = maximum_sharpe_ratio.round(2)
        del maximum_sharpe_ratio[maximum_sharpe_ratio.columns[1]]

        medium_portfolio = DataFrame([r_mean * 100], columns=self.df_close.columns, index=['доли, %']).T
        medium_portfolio['Цена сейчас'] = self.get_last_prices()
        medium_portfolio['Количество акций'] = ((medium_portfolio['доли, %'] / 100) * self.portfolio_cost) / medium_portfolio['Цена сейчас']
        medium_portfolio['Количество акций'] = medium_portfolio['Количество акций'].round(0)
        medium_portfolio = medium_portfolio.round(2)
        del medium_portfolio[medium_portfolio.columns[1]]

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
