import os
from flask import Flask, request
from utils.token_utils import get_access_token
from utils.data_utils import update_user_token, get_user_data, update_user_name
from utils.api_utils import get_user_info
import telebot
from dotenv import load_dotenv
from config import PORT
import logging
import hashlib
import secrets
import base64

load_dotenv()

app = Flask(__name__)
bot_token = os.getenv("BOT_TOKEN")
if not bot_token:
    print("Ошибка: токен бота не найден в файле .env")
    exit()
bot = telebot.TeleBot(bot_token)

logging.basicConfig(level=logging.DEBUG)


def generate_pkce_codes():
    code_verifier = secrets.token_urlsafe(100)
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode('utf-8').replace('=', '')
    return code_verifier, code_challenge



@app.route('/auth/callback')
def auth_callback():
    """Обрабатывает callback от Dodo IS."""
    code = request.args.get('code')
    user_id = request.args.get('state') #  state is used to send the user id
    logging.debug(f"Callback from Dodo IS. Code: {code}, User ID: {user_id}")
    user_data = get_user_data(int(user_id))
    if not user_data or not code :
        logging.error("Ошибка авторизации: Неверный запрос.")
        return "Ошибка авторизации: Неверный запрос.", 400
    code_verifier = user_data.get('code_verifier')
    access_token = get_access_token(int(user_id), code, code_verifier)
    if access_token:
        update_user_token(int(user_id), access_token)
        logging.info(f"Токен доступа успешно обновлен для пользователя {user_id}: {access_token}")
        user_info = get_user_info(access_token)
        logging.info(f"Информация о пользователе: {user_info}")
        if user_info and "name" in user_info:
           update_user_name(int(user_id), user_info["name"])
           bot.send_message(int(user_id), f"Вы успешно авторизованы, {user_info['name']}! Теперь напишите /start")
        else:
            bot.send_message(int(user_id), "Вы успешно авторизованы! Теперь напишите /start")
        return "Authorization Successful, please type /start in bot to continue", 200
    else:
      logging.error("Ошибка авторизации: Не удалось получить токен.")
      return "Ошибка авторизации: Не удалось получить токен.", 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True) # Port and host are just for testing.