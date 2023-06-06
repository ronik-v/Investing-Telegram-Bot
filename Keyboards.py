from aiogram.types import ReplyKeyboardMarkup
base_buttons = ['Помощь', 'Описание бота', 'Создать инвестиционный портфель', 'Создать график']
portfolio_buttons = ['Создать обычный портфель', 'Создать портфель с бета значением',
					'Создать портфель с максимальным доходом', 'Создать портфель с минимальной волатильностью']
graph_buttons = ['Создать график скользящих средних', 'Создать график японских свечей']


class Keyboard:
	@classmethod
	def create_base(clr) -> ReplyKeyboardMarkup:
		keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
		keyboard.add(*base_buttons)
		return keyboard

	@classmethod
	def create_portfolio(clr) -> ReplyKeyboardMarkup:
		keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
		keyboard.add(*portfolio_buttons)
		return keyboard

	@classmethod
	def create_graph(clr) -> ReplyKeyboardMarkup:
		keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
		keyboard.add(*graph_buttons)
		return keyboard
