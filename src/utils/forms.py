from aiogram.fsm.state import StatesGroup, State


class TickersListForms(StatesGroup):
    portfolio_type = State()
    portfolio_cost = State()
    tickers = State()


class TickerForm(StatesGroup):
    ticker = State()
