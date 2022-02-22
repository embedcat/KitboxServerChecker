import json
import logging
import os
import threading
import time
import requests
import telebot
from dotenv import load_dotenv


load_dotenv()

USERS_FILE = "users.json"
# SERVER_URL = "http://127.0.0.1:5000/api{num}"
SERVER_URL = "http://kitbox{num}.kit-invest.ru/KitBoxService.svc/SendRequest"

TIME_POLL_SEC = 90
TG_TOKEN = os.environ.get("TG_TOKEN")
EMOJI_OK = "\U0001f7E2"
EMOJI_FAIL = "\U0001f534"

MSG_SERVER_NOT_ANSWER = "{emoji} Сервер не отвечает. Ошибка: {error}"
MSG_SERVER_ERROR = "{emoji} Сервер не отвечает. Статус: {status}"
MSG_SERVER_OK = "{emoji} Сервер работает! Отлично!"
MSG_START = "Я буду присылать сообщения при изменении статуса сервера"
MSG_STOP = "Больше не буду беспокоить. Для возобновления рассылки присылай /start"
MSG_HELP = "/start - начать присылать уведомления о смене статуса сервера\n" \
           "/stop - не присылать уведомления о смене статуса сервера\n" \
           "/check - проверить сервер прямо сейчас\n" \
           "/stat - вывести статистику сервера\n" \
           "/help - показать эту справку"

telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(TG_TOKEN)

users = {}


def update_users_json():
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)


@bot.message_handler(commands=["start"])
def bot_start(message):
    user = {message.chat.username: str(message.chat.id)}
    users.update(user)
    update_users_json()
    bot.send_message(chat_id=message.chat.id, text=MSG_START)


@bot.message_handler(commands=["stop"])
def bot_stop(message):
    users.pop(message.chat.username)
    update_users_json()
    bot.send_message(chat_id=message.chat.id, text=MSG_STOP)


@bot.message_handler(commands=["help"])
def bot_help(message):
    bot.send_message(chat_id=message.chat.id, text=MSG_HELP)


@bot.message_handler(commands=["check"])
def bot_help(message):
    result = check_server_ok()
    msg = result_get_message(result=result)
    bot.send_message(chat_id=message.chat.id, text=msg)


def send_update_status(msg: str = "") -> None:
    for username, chat_id in users.items():
        bot.send_message(chat_id=chat_id, text=msg)
        time.sleep(0.2)


def check_server_ok() -> dict:
    for i in range(1, 5):
        url = SERVER_URL.format(num=i)
        try:
            r = requests.post(url=url)
        except requests.exceptions.RequestException as e:
            return {"result": False, "status": None, "error": str(e)}
        if r.status_code != 200:
            return {"result": False, "status": r.status_code, "error": None}
    return {"result": True}


def result_get_message(result: dict) -> str:
    if result["result"] is False:
        if result["status"] is None:
            return MSG_SERVER_NOT_ANSWER.format(emoji=EMOJI_FAIL, error=result["error"])
        else:
            return MSG_SERVER_ERROR.format(emoji=EMOJI_FAIL, status=result["status"])
    else:
        return MSG_SERVER_OK.format(emoji=EMOJI_OK)


def server_check_thread():
    is_first_iter = True
    server_status_ok = False

    while True:
        result = check_server_ok()
        msg = result_get_message(result=result)
        if (server_status_ok or is_first_iter) and result["result"] is False:
            send_update_status(msg=msg)
            server_status_ok = False
        elif (not server_status_ok or is_first_iter) and result["result"] is True:
            send_update_status(msg=msg)
            server_status_ok = True

        is_first_iter = False
        time.sleep(TIME_POLL_SEC)


if __name__ == "__main__":
    with open(USERS_FILE, "r") as file:
        users = json.load(file)

    t1 = threading.Thread(target=server_check_thread)
    t1.start()
    bot.infinity_polling()

