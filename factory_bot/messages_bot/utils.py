import requests
from .settings import TG_BOT_URL


def send_to_bot(chat_id, message):
    requests.post(TG_BOT_URL, json={
                "servermsg": {
                    "chat_id": chat_id,
                    "msg_text": message,
                }
            })
