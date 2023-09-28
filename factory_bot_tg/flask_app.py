from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import telepot
from urllib3 import ProxyManager
from logging import getLogger
import os
from dotenv import load_dotenv
import requests

app = Flask(__name__)
logger = getLogger(__name__)
env_res = load_dotenv()
TOKEN = os.getenv("TOKEN")
SECRET = os.getenv("SECRET")
HOST = os.getenv("HOST")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_DATABASENAME = os.getenv("DB_DATABASENAME")
SERVER_URL = os.getenv("SERVER_URL")


SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username=DB_USERNAME,
        password=DB_PASSWORD,
        hostname=DB_HOST,
        databasename=DB_DATABASENAME,
    )
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Token(db.Model):
    __tablename__ = "tokens"

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(4096))


def update_token_db(chat_id, token_text):
    existing_token = Token.query.get(chat_id)

    if existing_token and existing_token.token == token_text:
        return False

    if existing_token:
        existing_token.token = token_text
    else:
        token = Token(id=chat_id, token=token_text)
        db.session.add(token)
    try:
        db.session.commit()
        return True
    except Exception:
        return False


def update_token_server(chat_id, token_text):
    send_data = {
        "token_update": {
            "chat_id": chat_id,
            "token": token_text,
        }
    }
    logger.info("updating token %s for chat_id %s", token_text, chat_id)
    try:
        requests.post(SERVER_URL, json=send_data, timeout=10)
        return True
    except:
        logger.error("couldn't send new token to server for chat_id: %s", chat_id)
        return False


def parse_message(bot, chat_id, message):
    text = message.get("text", "")

    if text.startswith("/start"):
        return
    if text.startswith("/show_tokens"):
        tokens = Token.query.all()
        bot.sendMessage(chat_id, f"Tokens:\n{tokens}")
    else:
        token_updated = update_token_db(chat_id=chat_id, token_text=text)
        if token_updated:
            token_sent = update_token_server(chat_id=chat_id, token_text=text)


def get_tg_bot():
    # proxy settings
    proxy_url = "http://proxy.server:3128"
    telepot.api._pools = {
        'default': ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
    }
    telepot.api._onetime_pool_spec = (
        ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))

    webhook_url = f"https://{HOST}/{SECRET}"

    bot = telepot.Bot(TOKEN)
    if webhook_url != bot.getWebhookInfo()['url']:
        bot.setWebhook(webhook_url, max_connections=1)

    return bot


def send_message_from_server(bot, update):
    msg_info = update["servermsg"]
    chat_id = msg_info.get("chat_id")
    msg_text = msg_info.get("msg_text")

    try:
        logger.info("Got message: %s, %s", chat_id, msg_text)
        bot.sendMessage(int(chat_id), msg_text)
    except:
        logger.error("couldn't send message %s to chat with id %s", msg_text, chat_id)


@app.route('/{}'.format(SECRET), methods=["POST"])
def telegram_webhook():
    bot = get_tg_bot()

    update = request.get_json()
    if "servermsg" in update:
        send_message_from_server(bot, update)

    elif "message" in update:
        chat_id = update["message"]["chat"]["id"]
        message = update["message"]
        if "text" in message:
            parse_message(bot, chat_id, message)

    return "OK"
