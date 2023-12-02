import os
import schedule
import time

import telebot

from consts import ACCESS, TIME_SHEDULE_SEC, TOKKEN
from TransmissionConnection import TransmissionConnection

bot = telebot.TeleBot(TOKKEN)

tc = TransmissionConnection(
    os.environ.get("TRANSMISSION_URL", "localhost"),
    os.environ.get("TRANSMISSION_LOGIN", None),
    os.environ.get("TRANSMISSION_PASSWORD", None),
    int(os.environ.get("TRANSMISSION_PORT", 9091)),
)

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
                send_message(
                    f'Статус торрента "{torrent.name}" изменен: {old_status.to_emoji()} → {torrent.status.to_emoji()}'
                )
    torrents = new_torrents


if __name__ == "__main__":
    schedule.every(TIME_SHEDULE_SEC).seconds.do(periodic_event)
    while True:
        schedule.run_pending()
        time.sleep(1)
