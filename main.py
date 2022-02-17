import time

import requests

# SERVER_URL = 'http://127.0.0.1:5000/api'
SERVER_URL = 'http://kitbox1.kit-invest.ru/KitBoxService.svc/SendRequest'

TIME_POLL_SEC = 60

TG_TOKEN = '5154060556:AAFCeRYqle6fbNsh7Qa3EAPswK9i56NpVEc'
TG_CHAT_IDS = ['376585847']

EMOJI_OK = '\U0001f7E2'
EMOJI_FAIL = '\U0001f534'


def send_tg_msg(msg: str = '') -> None:
    for recipient in TG_CHAT_IDS:
        requests.post(
            url=f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': recipient, 'text': str(msg)}
        ).json()
        time.sleep(1)


def main():
    server_status_ok = False

    while True:
        try:
            r = requests.post(url=f'{SERVER_URL}')
        except requests.exceptions.RequestException:
            time.sleep(TIME_POLL_SEC)
            continue
        print(r.status_code)
        if server_status_ok and r.status_code != 200:
            msg = f"{EMOJI_FAIL} Server is down. Status code {r.status_code}"
            send_tg_msg(msg=msg)
            server_status_ok = False
        elif (not server_status_ok) and r.status_code == 200:
            msg = f'{EMOJI_OK} Server is OK. Awesome!'
            send_tg_msg(msg=msg)
            server_status_ok = True

        time.sleep(TIME_POLL_SEC)


if __name__ == '__main__':
    main()
