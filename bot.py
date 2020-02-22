import base64
import os
import time
from enum import Enum

import telebot
from telebot import types

from consts import TOKKEN, ACCESS, LIST_BUTTON_TEXT, list_keyboard
from TransmissionConnection import (TorrentStatus, TransmissionConnection,
                                    torrent_status_to_emoji)

bot = telebot.TeleBot(TOKKEN)


tc = TransmissionConnection(os.environ.get('TRANSMISSION_URL', 'localhost'), os.environ.get('TRANSMISSION_LOGIN', None), os.environ.get('TRANSMISSION_PASSWORD', None), os.environ.get('TRANSMISSION_PORT', 9091))

class AccessDeniedException(Exception):
    pass

def access(message):
    if message.from_user.id not in ACCESS:
        raise AccessDeniedException

def torrent_info(hashStr: str) -> (str, types.InlineKeyboardMarkup):
    torrent = tc[hashStr]
    keyboard = types.InlineKeyboardMarkup()
    if torrent.status == TorrentStatus.STOPPED:
        key_start = types.InlineKeyboardButton(text=f'Раздавать', callback_data=f'start_{torrent.hashStr}')
        keyboard.add(key_start)
    if torrent.status == TorrentStatus.SEEDING:
        key_pause = types.InlineKeyboardButton(text=f'Поставить на паузу', callback_data=f'pause_{torrent.hashStr}')
        keyboard.add(key_pause)
    key_del = types.InlineKeyboardButton(text=f'Удалить {torrent.name}', callback_data=f'del_{torrent.hashStr}')
    keyboard.add(key_del)
    text = f'{torrent.name}\nstatus: {torrent_status_to_emoji(torrent.status)}'
    return text, keyboard


def list_torrents(chat_id):
    for torrent in tc:
        text, keyboard = torrent_info(torrent.hashStr)
        bot.send_message(chat_id, text=text, reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def get_text_message(message):
    try:
        access(message)
        if message.text == '/help' or message.text == '/start':
            bot.send_message(message.from_user.id, 'Перешли мне торрент файл или магнет ссылку и я начну скачивание. Введи /list – для просмотра списка торрентов. Этим ботом могут пользоваться только доверенные лица', reply_markup=list_keyboard)
        elif message.text == '/list' or message.text == LIST_BUTTON_TEXT:
            list_torrents(message.from_user.id)
        elif message.text.startswith('magnet:'):
            tc.add_torrent(message.text)
            bot.send_message(message.from_user.id, f'{tc[-1].name} добавлен', reply_markup=list_keyboard)
    except AccessDeniedException:
        bot.send_message(message.from_user.id, 'Этот бот не для тебя') 


@bot.message_handler(content_types=['document'])
def get_document_message(message):
    try:
        access(message)
        if len(message.document.file_name) < 8 or message.document.file_name[-7:] != 'torrent':
            bot.send_message(message.from_user.id, 'Можно мне отправить только torrent файл')
        file_info = bot.get_file(message.document.file_id)
        new_torrent = bot.download_file(file_info.file_path)
        new_torrent = base64.b64encode(bytes(new_torrent)).decode('utf-8')
        tc.add_torrent(new_torrent)
        bot.send_message(message.from_user.id, f'{tc[-1].name} добавлен', reply_markup=list_keyboard)
    except AccessDeniedException:
        bot.send_message(message.from_user.id, 'Этот бот не для тебя') 

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    for torrent in tc:
        if call.data == f'del_{torrent.hashStr}':
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text=f'Да', callback_data=f'del_agree_{torrent.hashStr}'))
            keyboard.add(types.InlineKeyboardButton(text=f'Нет', callback_data=f'del_disagree_{torrent.hashStr}'))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"ТЫ УВЕРЕН?", reply_markup=keyboard)
        elif call.data == f'pause_{torrent.hashStr}':
            tc.stop_torrent(torrent)
            text, keyboard = torrent_info(torrent.hashStr)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard)
        elif call.data == f'del_disagree_{torrent.hashStr}':
            info, keyboard = torrent_info(torrent.hashStr)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=info, reply_markup=keyboard)
        elif call.data == f'del_agree_{torrent.hashStr}':
            tc.del_torrent(torrent, delete_data=True)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{torrent.name} удален")
        elif call.data == f'start_{torrent.hashStr}':
            tc.start_torrent(torrent)
            text, keyboard = torrent_info(torrent.hashStr)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=keyboard)
        elif call.data == 'list':
            list_torrents(call.message.chat.id)

if __name__ == "__main__":
    bot.polling(none_stop=True)
