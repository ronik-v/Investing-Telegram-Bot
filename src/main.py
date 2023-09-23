from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from aiogram import Bot, types
import aiogram.utils.markdown as md

from PortfolioFilters import BetaPositivePortfolioFilter, IncomeTickerFilter, VolatilityTickerFilter
from PriceСharts import TickerDynamics, JapaneseCandlesDynamics
from PortfolioModels import MarkovModel
from TickerDataParser import DataParser
from Keyboards import Keyboard, portfolio_buttons, graph_buttons

from available_messages import START_COMMAND, HELP_COMMAND, DESCRIPTION_COMMAND
from forms import TickersListForms, TickerForm
from datetime import datetime, timedelta
from config import bot_token
import logging

from redis import StrictRedis


bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
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
	print(f'main - {getcwd()}')
except OSError:
	print('\033[31m {}'.format('Failed to change directory to Graphs.'))
	exit(1)

P_COMMAND = {}
P_COST = {}
G_COMMAND = {}


# Dates for parser
def current_dates() -> tuple[datetime, datetime]:
	today = datetime.now()
	end_date = today - timedelta(weeks=10)  # ~3 months earlier
	return today, end_date


#   Delete data from dict
def delete_dict(_dict: dict) -> None:
	for key in list(_dict.keys()):
		del _dict[key]


#   Data sending functions
async def send_text(message: types.Message, structure: list) -> None:
	for mes in structure:
		await bot.send_message(message.chat.id, md.text(mes))


async def send_photo(message: types.Message, png_file) -> None:
	with open(png_file, 'rb') as photo:
		await bot.send_photo(message.chat.id, photo)


#   Bot verification
"""
The function must be synchronous since processing in the event loop does not always have time
"""


def bot_blocker(message: types.Message) -> None:
	if 'bot' in message.from_user.username.lower():
		log_message_bot = f'BOT! -> {message.from_user.id}-{message.from_user.username}'
		# Will hold id for up to an hour
		_redis.set(message.from_user.id, log_message_bot, 3600)
		logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
		logging.warning(log_message_bot)
	else:
		"""
		User activity information
		"""
		log_message_user = f'USER -> {message.from_user.id}-{message.from_user.username}'
		logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
		logging.info(log_message_user)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
	bot_blocker(message)
	if _redis.exists(message.from_user.id):
		pass
	else:
		await bot.send_message(
			reply_markup=Keyboard.create_base(),
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


@dp.message_handler(lambda message: message.text == 'Создать инвестиционный портфель')
async def create_portfolio(message: types.Message):
	await bot.send_message(
		chat_id=message.from_user.id,
		reply_markup=Keyboard.create_portfolio(),
		text='Выберите тип инвестиционного портфеля на клавиатуре'
	)


@dp.message_handler(lambda message: message.text in portfolio_buttons)
async def create_portfolio_command(message: types.Message):
	P_COMMAND[message.from_user.id] = message.text
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
		P_COST[message.from_user.id] = float(message.text)
		await TickersListForms.next()
		await message.reply('Перечислите название тикеров через запятую')
	except:
		logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
		logging.error(f'cost {message.from_user.id}-{message.from_user.first_name} => MESSAGE {message.text}')
		await state.finish()
		await message.reply('Стоймость портфеля была введена не верно')


@dp.message_handler(state=TickersListForms.tickers)
async def portfolio_result(message: types.Message, state: FSMContext):
	today, end_date = current_dates()
	date_start, date_end = end_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
	try:
		tickers = message.text.split(',')
		command = P_COMMAND[message.from_user.id]
		cost = P_COST[message.from_user.id]
		for position in range(len(tickers)):
			ticker = tickers[position].upper()
			if ticker[:1] == ' ':
				tickers[position] = ticker[1:]
		if command == 'Создать обычный портфель':
			markov_p = MarkovModel(DataParser(tickers, date_start, date_end).parse_tickers(), cost).result()
			await send_text(message, markov_p)
		if command == 'Создать портфель с бета значением':
			beta_tickers = BetaPositivePortfolioFilter(tickers, date_start, date_end).filter()
			markov_p_beta = MarkovModel(DataParser(beta_tickers, date_start, date_end).parse_tickers(), cost).result()
			await send_text(message, markov_p_beta)
		if command == 'Создать портфель с максимальным доходом':
			income_tickers = IncomeTickerFilter(tickers, date_start, date_end).filter()
			markov_p_income = MarkovModel(DataParser(income_tickers, date_start, date_end).parse_tickers(), cost).result()
			await send_text(message, markov_p_income)
		if command == 'Создать портфель с минимальной волатильностью':
			volatility_tickers = VolatilityTickerFilter(tickers, date_start, date_end).filter()
			markov_p_volatility = MarkovModel(DataParser(volatility_tickers, date_start, date_end).parse_tickers(), cost).result()
			await send_text(message, markov_p_volatility)
		if len(P_COMMAND) > 2000 and len(P_COST) > 2000:
			delete_dict(P_COMMAND)
			delete_dict(P_COST)
	except:
		logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
		logging.error(f'portfolio {message.from_user.id}-{message.from_user.first_name} => MESSAGE {message.text}')
	finally:
		await state.finish()
		await bot.send_message(
			reply_markup=Keyboard.create_base(),
			chat_id=message.from_user.id,
			text='Что бы вы хотели еще узнать?'
		)


@dp.message_handler(lambda message: message.text == 'Создать график')
async def create_graph(message: types.Message):
	await bot.send_message(
		chat_id=message.from_user.id,
		reply_markup=Keyboard.create_graph(),
		text='Выберите тип графика на клавиатуре'
	)


@dp.message_handler(lambda message: message.text in graph_buttons)
async def create_graph_command(message: types.Message):
	G_COMMAND[message.from_user.id] = message.text
	await TickerForm.ticker.set()
	await message.answer('Напишите название тикера')


@dp.message_handler(state=TickerForm)
async def graph_result(message: types.Message, state: FSMContext):
	today, end_date = current_dates()
	date_start, date_end = end_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
	try:
		ticker = message.text.upper()
		command = G_COMMAND[message.from_user.id]
		if command == 'Создать график скользящих средних':
			file = TickerDynamics(ticker, date_start, date_end, message.from_id).png_file_path()
			await send_photo(message, file)
		if command == 'Создать график японских свечей':
			file = JapaneseCandlesDynamics(ticker, date_start, date_end, message.from_id).png_file_path()
			await send_photo(message, file)
		if len(G_COMMAND) > 2000:
			delete_dict(G_COMMAND)
	except:
		logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
		logging.error(f'graph {message.from_user.id}-{message.from_user.first_name} => MESSAGE {message.text}')
	finally:
		await state.finish()
		await bot.send_message(
			reply_markup=Keyboard.create_base(),
			chat_id=message.from_user.id,
			text='Что бы вы хотели еще узнать?'
		)


def main() -> None:
	try:
		executor.start_polling(dp, skip_updates=True)
	except OSError as err:
		logging.error(err)
		exit(1)
	finally:
		print('Bot dropped.')


if __name__ == '__main__':
	main()
