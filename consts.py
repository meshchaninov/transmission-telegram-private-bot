import os

from telebot import apihelper, types

TOKKEN = os.environ.get('TOKEN')
ACCESS = set(int(i) for i in os.environ.get('ACCESS', '').split(':'))

LIST_BUTTON_TEXT = 'Список'
list_keyboard = types.ReplyKeyboardMarkup()
list_keyboard.add(types.KeyboardButton(text=LIST_BUTTON_TEXT))

TIME_SHEDULE_SEC = int(os.environ.get('TIME_SHEDULE_SEC', 600))

apihelper.proxy = {
    'https': f'socks5://{os.environ.get("SOCKS5_LOGIN")}:{os.environ.get("SOCKS5_PASSWORD")}@{os.environ.get("SOCKS5_ADDRESS")}'
}
