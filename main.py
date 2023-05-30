from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import ReplyKeyboardMarkup
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from aiogram import Bot, types
import aiogram.utils.markdown as md

from PortfolioFilters import MakeBetaPositivePortfolio, IncomeTickerFilter, VolatilityTickerFilter
from PriceСharts import TickerDynamics, JapaneseCandlesDynamics
from PortfolioModels import MarkovModel
from TickerDataParser import DataParser

from available_messages import START_COMMAND, HELP_COMMAND, DESCRIPTION_COMMAND
from forms import TickersListForms, TickerForm
from datetime import datetime, timedelta
from config import bot_token
import logging

today = datetime.now()
end_date = today - timedelta(weeks=10)  # ~3 months earlier
date_start, date_end = end_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
logger = logging.getLogger(__name__)

try:
    from os import chdir, getcwd

    chdir('Graphs')
    print(f'main - {getcwd()}')
except OSError:
    print("\033[31m {}".format("Failed to change directory to Graphs."))
    exit(1)

P_COMMAND = []
P_COST = []
G_COMMAND = []


#   Data sending functions
async def send_text(message: types.Message, structure: list):
    for mes in structure:
        await bot.send_message(message.chat.id, md.text(mes))


async def send_photo(message: types.Message, png_file):
    with open(png_file, 'rb') as photo:
        await bot.send_photo(message.chat.id, photo)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    systems_buttons = ['Помощь', 'Описание бота']
    portfolios_buttons = ['Создать обычный портфель', 'Создать портфель с бета значением',
                          'Создать портфель с максимальным доходом', 'Создать портфель с минимальной волатильностью', ]
    graphs_buttons = ['Создать график скользящих средних', 'Создать график японских свечей']
    keyboard.add(systems_buttons[0])
    keyboard.add(systems_buttons[1]).insert(portfolios_buttons[0]).insert(portfolios_buttons[1]).insert(
        portfolios_buttons[2]).insert(portfolios_buttons[3])
    keyboard.add(*graphs_buttons)
    await bot.send_message(
        reply_markup=keyboard,
        chat_id=message.from_user.id,
        text=START_COMMAND,
        parse_mode='HTML'
    )


@dp.message_handler(lambda message: message.text == 'Помощь')
async def help_command(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id,
        text=HELP_COMMAND,
        parse_mode='HTML'
    )


@dp.message_handler(lambda message: message.text == 'Описание бота')
async def description_command(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id,
        text=DESCRIPTION_COMMAND,
        parse_mode='HTML'
    )


@dp.message_handler(lambda message: message.text in [
    'Создать обычный портфель', 'Создать портфель с бета значением',
    'Создать портфель с максимальным доходом', 'Создать портфель с минимальной волатильностью'])
async def create_portfolio_command(message: types.Message):
    P_COMMAND.append(message.text)
    await TickersListForms.portfolio_cost.set()
    await message.answer('Введите стоймость вашего портфеля')


@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('ОК')


@dp.message_handler(state=TickersListForms.portfolio_cost)
async def portfolio_cost_handler(message: types.Message, state: FSMContext):
    try:
        P_COST.append(float(message.text))
        await TickersListForms.next()
        await message.reply('Перечислите название тикеров через запятую')
    except:
        logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
        logging.info(f'cost {message.from_user.id}-{message.from_user.first_name}')
        await state.finish()
        await message.reply('Стоймость портфеля была введена не верно')


"""
Creation of investment portfolios according to certain models - "filters" of ordinary shares
"Filters" of ordinary shares see in PortfolioFilters.py
"""

@dp.message_handler(state=TickersListForms.tickers)
async def portfolio_result(message: types.Message, state: FSMContext):
    try:
        tickers = message.text.split(',')
        command = P_COMMAND[len(P_COMMAND) - 1]
        cost = P_COST[len(P_COST) - 1]
        for position in range(len(tickers)):
            ticker = tickers[position].upper()
            if ticker[:1] == " ":
                tickers[position] = ticker[1:]
        if command == 'Создать обычный портфель':
            markov_p = MarkovModel(DataParser(tickers, date_start, date_end).parse_tickers(), cost).result()
            await send_text(message, markov_p)
        if command == 'Создать портфель с бета значением':
            beta_tickers = MakeBetaPositivePortfolio(tickers, date_start, date_end).BetaPositivePortfolio(tickers,
                                                                                                          date_start,
                                                                                                          date_end)
            markov_p_beta = MarkovModel(DataParser(beta_tickers, date_start, date_end).parse_tickers(), cost).result()
            await send_text(message, markov_p_beta)
        if command == 'Создать портфель с максимальным доходом':
            income_tickers = IncomeTickerFilter(tickers, date_start, date_end).income_filter()
            markov_p_income = MarkovModel(DataParser(income_tickers, date_start, date_end).parse_tickers(),
                                          cost).result()
            await send_text(message, markov_p_income)
        if command == 'Создать портфель с минимальной волатильностью':
            volatility_tickers = VolatilityTickerFilter(tickers, date_start, date_end).filter()
            markov_p_volatility = MarkovModel(DataParser(volatility_tickers, date_start, date_end).parse_tickers(),
                                              cost).result()
            await send_text(message, markov_p_volatility)
        if len(P_COMMAND) > 2000 and len(P_COST) > 2000:
            del P_COMMAND[:]
            del P_COST[:]
    except:
        logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
        logging.info(f'portfolio {message.from_user.id}-{message.from_user.first_name}')
        await state.finish()
    finally:
        await state.finish()


@dp.message_handler(lambda message: message.text in ['Создать график скользящих средних',
                                                     'Создать график японских свечей'])
async def create_graph_command(message: types.Message):
    G_COMMAND.append(message.text)
    await TickerForm.ticker.set()
    await message.answer('Напишите название тикера')

"""
Analysis of the dynamics at the moment consists of two types of graphs:
1. Moving averages based on which you can determine the current trend in the development of the price of an asset;
2. Japanese candlesticks based on which you can determine the pattern of behavior of short-term dynamics.
"""

@dp.message_handler(state=TickerForm)
async def graph_result(message: types.Message, state: FSMContext):
    try:
        ticker = message.text.upper()
        command = G_COMMAND[len(G_COMMAND) - 1]
        if command == 'Создать график скользящих средних':
            file = TickerDynamics(ticker, date_start, date_end, message.from_id).dynamics_graph()
            await send_photo(message, file)
        if command == 'Создать график японских свечей':
            file = JapaneseCandlesDynamics(ticker, date_start, date_end, message.from_id).candles_graph()
            await send_photo(message, file)
        if len(G_COMMAND) > 2000:
            del G_COMMAND[:]
    except:
        logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
        logging.info(f'graph {message.from_user.id}-{message.from_user.first_name}')
        await state.finish()
    finally:
        await state.finish()


def main() -> None:
    try:
        executor.start_polling(dp, skip_updates=True)
    except OSError as Error:
        print(Error)
        exit(1)
    finally:
        print('Bot dropped.')


if __name__ == '__main__':
    main()
