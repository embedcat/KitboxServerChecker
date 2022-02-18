import time
import requests

# SERVER_URL = 'http://127.0.0.1:5000/api{num}'
SERVER_URL = 'http://kitbox{num}.kit-invest.ru/KitBoxService.svc/SendRequest'

TIME_POLL_SEC = 90

TG_TOKEN = '5154060556:AAFCeRYqle6fbNsh7Qa3EAPswK9i56NpVEc'
TG_CHAT_IDS = ['376585847', '753407442']

EMOJI_OK = '\U0001f7E2'
EMOJI_FAIL = '\U0001f534'


def send_tg_msg(msg: str = '') -> None:
    for recipient in TG_CHAT_IDS:
        requests.post(
            url=f'https://api.telegram.org/bot{TG_TOKEN}/sendMessage',
            data={'chat_id': recipient, 'text': str(msg)}
        ).json()
        time.sleep(1)


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


def main():
    server_status_ok = False

    while True:
        result = check_server_ok()
        if server_status_ok and result['result'] is False:
            if result['status'] is None:
                msg = f"{EMOJI_FAIL} Server is down. Server error {result['error']}"
            else:
                msg = f"{EMOJI_FAIL} Server is down. Status code {result['status_code']}"
            send_tg_msg(msg=msg)
            server_status_ok = False
        elif (not server_status_ok) and result['result'] is True:
            msg = f'{EMOJI_OK} Server is OK. Awesome!'
            send_tg_msg(msg=msg)
            server_status_ok = True

        time.sleep(TIME_POLL_SEC)


if __name__ == '__main__':
    main()
