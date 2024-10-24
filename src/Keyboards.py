from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

base_buttons = ['Помощь', 'Описание бота', 'Создать инвестиционный портфель', 'Создать график']
portfolio_buttons = ['Создать обычный портфель', 'Создать портфель с бета значением',
                     'Создать портфель с максимальным доходом', 'Создать портфель с минимальной волатильностью']
graph_buttons = ['Создать график скользящих средних', 'Создать график японских свечей']


class Keyboard:
    @classmethod
    def create_base(cls) -> ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text=button_text)] for button_text in base_buttons
        ], resize_keyboard=True)
        return keyboard

    @classmethod
    def create_portfolio(cls) -> ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text=button_text)] for button_text in portfolio_buttons
        ], resize_keyboard=True)
        return keyboard

    @classmethod
    def create_graph(cls) -> ReplyKeyboardMarkup:
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text=button_text)] for button_text in graph_buttons
        ], resize_keyboard=True)
        return keyboard
