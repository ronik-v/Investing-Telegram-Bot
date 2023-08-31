from pandas import DataFrame
import numpy as np


class MarkovModel:
    def __init__(self, df_close, portfolio_cost):
        self.df_close = df_close
        self.portfolio_cost = portfolio_cost
        self.df_close_data = df_close.pct_change()
        self.df_close_mean = self.df_close_data.mean()
        self.cov_matrix = self.df_close_data.cov()
        self.tickers_amount = len(self.df_close.columns)
        self.portfolio_structure = list()

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

    def result(self) -> list:
        iterations = 800
        risk = np.zeros(iterations)
        doh = np.zeros(iterations)
        portf = np.zeros((iterations, self.tickers_amount))

        for it in range(iterations):
            r = self.random_portfolio()
            portf[it, :] = r
            risk[it] = self.risk_of_portfolio(r)
            doh[it] = self.profitability_of_portfolio(r)

        min_risk = np.argmin(risk)
        max_sharp_koef = np.argmax(doh / risk)

        r_mean = np.ones(self.tickers_amount) / self.tickers_amount
        risk_mean = self.risk_of_portfolio(r_mean)
        doh_mean = self.profitability_of_portfolio(r_mean)

        MinimalRisk = DataFrame([portf[min_risk] * 100], columns=self.df_close.columns, index=['доли, %']).T
        MinimalRisk['Цена сейчас'] = self.get_last_prices()
        MinimalRisk['Количество акций'] = ((MinimalRisk['доли, %'] / 100) * self.portfolio_cost) / MinimalRisk['Цена сейчас']
        MinimalRisk['Количество акций'] = MinimalRisk['Количество акций'].round(0)
        MinimalRisk = MinimalRisk.round(2)
        del MinimalRisk[MinimalRisk.columns[1]]

        MaximumSharpeRatio = DataFrame([portf[max_sharp_koef] * 100], columns=self.df_close.columns, index=['доли, %']).T
        MaximumSharpeRatio['Цена сейчас'] = self.get_last_prices()
        MaximumSharpeRatio['Количество акций'] = ((MaximumSharpeRatio['доли, %'] / 100) * self.portfolio_cost) / MaximumSharpeRatio['Цена сейчас']
        MaximumSharpeRatio['Количество акций'] = MaximumSharpeRatio['Количество акций'].round(0)
        MaximumSharpeRatio = MaximumSharpeRatio.round(2)
        del MaximumSharpeRatio[MaximumSharpeRatio.columns[1]]

        MediumPortfolio = DataFrame([r_mean * 100], columns=self.df_close.columns, index=['доли, %']).T
        MediumPortfolio['Цена сейчас'] = self.get_last_prices()
        MediumPortfolio['Количество акций'] = ((MediumPortfolio['доли, %'] / 100) * self.portfolio_cost) / MediumPortfolio['Цена сейчас']
        MediumPortfolio['Количество акций'] = MediumPortfolio['Количество акций'].round(0)
        MediumPortfolio = MediumPortfolio.round(2)
        del MediumPortfolio[MediumPortfolio.columns[1]]

        self.portfolio_structure.append('Минимальный риск\n')
        self.portfolio_structure.append("риск = %1.2f%%" % (float(risk[min_risk]) * 100.))
        self.portfolio_structure.append(MinimalRisk)
        self.portfolio_structure.append('\nМаксимальный коэффициент Шарпа\n')
        self.portfolio_structure.append("риск = %1.2f%%" % (float(risk[max_sharp_koef]) * 100.))
        self.portfolio_structure.append(MaximumSharpeRatio)
        self.portfolio_structure.append('\nСредний портфель\n')
        self.portfolio_structure.append("риск = %1.2f%%" % (float(risk_mean) * 100.))
        self.portfolio_structure.append(MediumPortfolio)
        return self.portfolio_structure
