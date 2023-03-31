"""
commands = ["/less", "/beta", "/incm", "/volt"] - Фильтры: без фильтра, бета, по доходности, по волатильности.
"/stic" - График динамики цены тикера.
"""
# TODO Сделать кнопки и вывод графика японских свечей.
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram import Bot, types

from PortfolioFilters import MakeBetaPositivePortfolio, IncomeTickerFilter, VolatilityTickerFilter
from PortfolioModels import MarkovModel
from PriceСharts import TickerDynamics
from TickerDataParser import DataParser

from config import bot_token
from datetime import datetime, timedelta

today = datetime.now()
end_date = today - timedelta(weeks=12)  # 3 months earlier
date_start, date_end = end_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
bot = Bot(token=bot_token)
dp = Dispatcher(bot)
try:
    from os import chdir

    chdir('Graphs')
except OSError:
    print("\033[31m {}".format("Failed to change directory to Graphs."))
    exit(1)


async def send(message: types.Message, structure: list):
    for mes in structure:
        await bot.send_message(message.from_id, mes)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Привет!\n"
                        "Данный бот помогает узнать оптимальную, на данный момент, структуру инвестиционного портфеля.\n"
                        "Вы можете использовать специальные алгоритмы отбора активов: /beta, /incm, /volt "
                        "(отбор по бета значению, отбор по доходности, отбор по волатильности).\n"
                        "Если не желаете использовать алгоритмы пропишите /less.\n"
                        "Также данный бот может вывести график цены актива и скользящих средних командой /stic.\n"
                        "Примеры использования команд - (\n"
                        "/less=SBER, GAZP, YNDX, ROSN, VTBR\n/beta=SBER, GAZP, YNDX, ROSN, VTBR\n"
                        "/stic=SBER).")


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Скажите, что вам необходимо узнать?")


@dp.message_handler()
async def bot_realise(message: types.Message):
    tickers = None
    try:
        tickers = message.text[6:].split(",")
        for position in range(len(tickers)):
            ticker = tickers[position]
            if ticker[:1] == " ":
                tickers[position] = ticker[1:]
    except TypeError:
        await bot.send_message(message.from_id, "Простите, но вы неправильно ввели список тикеров или тикер.")
    match message.text[:5]:
        case "/less":
            markov_p = MarkovModel(DataParser(tickers, date_start, date_end).parse_tickers()).result()
            await send(message, markov_p)
        case "/beta":
            beta_tickers = MakeBetaPositivePortfolio(tickers, date_start, date_end).BetaPositivePortfolio(tickers,
                                                                                                          date_start,
                                                                                                          date_end)
            markov_p_beta = MarkovModel(DataParser(beta_tickers, date_start, date_end).parse_tickers()).result()
            await send(message, markov_p_beta)
        case "/incm":
            income_tickers = IncomeTickerFilter(tickers, date_start, date_end).income_filter()
            markov_p_income = MarkovModel(DataParser(income_tickers, date_start, date_end).parse_tickers()).result()
            await send(message, markov_p_income)
        case "/volt":
            volatility_tickers = VolatilityTickerFilter(tickers, date_start, date_end).filter()
            markov_p_volatility = MarkovModel(
                DataParser(volatility_tickers, date_start, date_end).parse_tickers()).result()
            await send(message, markov_p_volatility)
        case "/stic":
            png = open(TickerDynamics(tickers[0], date_start, date_end, message.from_id).dynamics_graph(), "rb")
            await bot.send_photo(message.from_id, png)


if __name__ == '__main__':
    try:
        executor.start_polling(dp)
    except OSError as Error:
        print(Error)
