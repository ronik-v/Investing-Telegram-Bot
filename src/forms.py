from aiogram.dispatcher.filters.state import State, StatesGroup


class TickersListForms(StatesGroup):
    portfolio_cost = State()
    tickers = State()


class TickerForm(StatesGroup):
    ticker = State()
