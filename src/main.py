from asyncio import run
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown as md
from aiogram.types import BufferedInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from portfolio_filters import BetaPositivePortfolioFilter, IncomeTickerFilter, VolatilityTickerFilter
from portfolio_models import MarkovModel
from keyboards import Keyboard
from available_messages import START_COMMAND, HELP_COMMAND, DESCRIPTION_COMMAND
from forms import TickersListForms
from datetime import datetime, timedelta
from config import bot_token
import logging
from redis import StrictRedis
from price_charts import TickerDynamics, JapaneseCandlesDynamics

bot = Bot(token=bot_token)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
_redis = StrictRedis(
    host='127.0.0.1',
    port=6379,
    charset='utf-8',
    decode_responses=True
)
logger = logging.getLogger(__name__)

try:
    from os import chdir, getcwd
    chdir('src/Graphs')
    logger.info(f'main - {getcwd()}')
except OSError:
    try:
        chdir('Graphs')
        logger.info(f'main - {getcwd()}')
    except OSError:
        logger.error('Failed to change directory to Graphs.')
        exit(1)

P_COMMAND = {}
P_COST = {}
G_COMMAND = {}


def current_dates() -> tuple[datetime, datetime]:
    today = datetime.now()
    end_date = today - timedelta(weeks=12)  # ~3 months earlier
    return today, end_date


def delete_dict(_dict: dict) -> None:
    _dict.clear()


async def send_text(message: types.Message, structure: list) -> None:
    for mes in structure:
        await bot.send_message(message.chat.id, md.text(mes))


async def send_photo(message: types.Message, image_data: bytes, file_name: str) -> None:
    try:
        image_file = BufferedInputFile(image_data, filename=file_name)
        await bot.send_photo(message.chat.id, image_file)
    except Exception as ex:
        logger.error(f"Ошибка отправка файла: {ex}")


def bot_blocker(message: types.Message) -> None:
    if 'bot' in message.from_user.username.lower():
        log_message = f'BOT! -> {message.from_user.id}-{message.from_user.username}'
        _redis.set(message.from_user.id, log_message, 3600)
        logger.warning(log_message)
    else:
        log_message = f'USER -> {message.from_user.id}-{message.from_user.username}'
        logger.info(log_message)


@dp.message(Command(commands=['start']))
async def start_command(message: types.Message):
    bot_blocker(message)
    if not _redis.exists(message.from_user.id):
        await bot.send_message(
            chat_id=message.from_user.id,
            text=START_COMMAND,
            parse_mode='HTML',
            reply_markup=Keyboard.create_base()
        )


@dp.message(F.text == 'Помощь')
async def help_command(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id,
        text=HELP_COMMAND,
        parse_mode='HTML'
    )


@dp.message(F.text == 'Описание бота')
async def description_command(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id,
        text=DESCRIPTION_COMMAND,
        parse_mode='HTML'
    )


@dp.message(F.text == 'Создать инвестиционный портфель')
async def create_portfolio(message: types.Message, state: FSMContext):
    await state.set_state(TickersListForms.portfolio_type)
    await bot.send_message(
        chat_id=message.from_user.id,
        reply_markup=Keyboard.create_portfolio(),
        text='Выберите тип инвестиционного портфеля на клавиатуре'
    )


@dp.message(TickersListForms.portfolio_type)
async def change_portfolio_type(message: types.Message, state: FSMContext):
    try:
        P_COMMAND[message.from_user.id] = message.text
        await state.set_state(TickersListForms.portfolio_cost)
        await message.reply("Укажите стоймость портфеля")

    except Exception as ex:
        logger.error(f"Ошибка выбора типа портфеля: {ex}")


@dp.message(TickersListForms.portfolio_cost)
async def portfolio_cost_handler(message: types.Message, state: FSMContext):
    await state.set_state(TickersListForms.tickers)

    try:
        P_COST[message.from_user.id] = float(message.text)
        await message.reply('Перечислите название тикеров через запятую')
    except ValueError:
        logger.error(f'Non-numeric input: {message.from_user.id} -> {message.text}')
        await message.reply('Стоимость портфеля была введена неверно. Введите числовое значение.')


@dp.message(TickersListForms.tickers)
async def portfolio_result(message: types.Message, state: FSMContext):
    today, end_date = current_dates()
    date_start, date_end = end_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')

    try:
        tickers = [ticker.strip().upper() for ticker in message.text.split(',')]
        command = P_COMMAND[message.from_user.id]
        cost = P_COST.get(message.from_user.id)

        if command == 'Создать обычный портфель':
            markov_p = MarkovModel(tickers, date_start, date_end, cost).result()
            await send_text(message, markov_p)

        elif command == 'Создать портфель с бета значением':
            beta_tickers = BetaPositivePortfolioFilter(tickers, date_start, date_end).filter()
            markov_p_beta = MarkovModel(beta_tickers, date_start, date_end, cost).result()
            await send_text(message, markov_p_beta)

        elif command == 'Создать портфель с максимальным доходом':
            income_tickers = IncomeTickerFilter(tickers, date_start, date_end).filter()
            markov_p_income = MarkovModel(income_tickers, date_start, date_end, cost).result()
            await send_text(message, markov_p_income)

        elif command == 'Создать портфель с минимальной волатильностью':
            volatility_tickers = VolatilityTickerFilter(tickers, date_start, date_end).filter()
            markov_p_volatility = MarkovModel(volatility_tickers, date_start, date_end, cost).result()
            await send_text(message, markov_p_volatility)

        if len(P_COMMAND) > 2000 and len(P_COST) > 2000:
            delete_dict(P_COMMAND)
            delete_dict(P_COST)
    except Exception as ex:
        logger.error(f"Portfolio creation error: {ex}")
    finally:
        await state.clear()
        await bot.send_message(
            chat_id=message.from_user.id,
            text='Что бы вы хотели еще узнать?',
            reply_markup=Keyboard.create_base()
        )


@dp.message(F.text == 'Создать график')
async def create_graph(message: types.Message):
    await bot.send_message(
        chat_id=message.from_user.id,
        reply_markup=Keyboard.create_graph(),
        text='Выберите тип графика на клавиатуре'
    )


@dp.message(F.text.startswith('Создать график'))
async def create_graph_command(message: types.Message):
    G_COMMAND[message.from_user.id] = message.text
    await message.answer('Напишите название тикера')


@dp.message(F.text.isupper())
async def graph_result(message: types.Message, state: FSMContext):
    today, end_date = current_dates()
    date_start, date_end = end_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    try:
        ticker = message.text.upper()
        command = G_COMMAND.get(message.from_user.id)

        if command == 'Создать график скользящих средних':
            img_data, file_name = TickerDynamics(ticker, date_start, date_end, message.from_user.id).png_file_path()
            await send_photo(message, img_data, file_name)

        elif command == 'Создать график японских свечей':
            img_data, file_name = JapaneseCandlesDynamics(ticker, date_start, date_end, message.from_user.id).png_file_path()
            await send_photo(message, img_data, file_name)

        if len(G_COMMAND) > 2000:
            delete_dict(G_COMMAND)
    except Exception as ex:
        logger.error(f"Graph creation error: {ex}")
    finally:
        await state.clear()
        await bot.send_message(
            chat_id=message.from_user.id,
            text='Что бы вы хотели еще узнать?',
            reply_markup=Keyboard.create_base()
        )


async def main() -> None:
    try:
        await dp.start_polling(bot)
    except OSError as err:
        logger.error(err)
        exit(1)
    finally:
        print('Bot dropped.')


if __name__ == '__main__':
    run(main())
