import datetime
import os
import sched
import schedule
import time
from functools import wraps
from threading import Thread

import telebot

from consts import ACCESS, TIME_SHEDULE_SEC, TOKKEN, list_keyboard
from TransmissionConnection import (TransmissionConnection,
                                    torrent_status_to_emoji)

bot = telebot.TeleBot(TOKKEN)

tc = TransmissionConnection(os.environ.get('TRANSMISSION_URL', 'localhost'), os.environ.get('TRANSMISSION_LOGIN', None), os.environ.get('TRANSMISSION_PASSWORD', None), os.environ.get('TRANSMISSION_PORT', 9091))

torrents, _ = tc.get_torrents()


def send_message(message):
    for user in ACCESS:
        bot.send_message(user, message)


def periodic_event():
    global torrents
    old_tor_hash = {t.hashStr: t for t in torrents}
    old_tor_hash_keys = set(old_tor_hash.keys())
    new_torrents, _ = tc.get_torrents()
    for torrent in new_torrents:
        if torrent.hashStr in old_tor_hash_keys:
            old_status = old_tor_hash[torrent.hashStr].status
            if torrent.status != old_status:
                send_message(f'Статус торрента "{torrent.name}" изменен: {torrent_status_to_emoji(old_status)} → {torrent_status_to_emoji(torrent.status)}')
    torrents = new_torrents

if __name__ == "__main__":
    schedule.every(TIME_SHEDULE_SEC).seconds.do()
    while True:
        schedule.run_pending()
        time.sleep(1)
