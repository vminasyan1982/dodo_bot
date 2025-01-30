import os
from flask import Flask, request
from utils.token_utils import get_access_token
from utils.data_utils import update_user_token, get_user_data, update_user_name
from utils.api_utils import get_user_info
import telebot
from dotenv import load_dotenv
from config import PORT
load_dotenv()

app = Flask(__name__)
bot_token = os.getenv("BOT_TOKEN")
if not bot_token:
    print("Ошибка: токен бота не найден в файле .env")
    exit()
bot = telebot.TeleBot(bot_token)

@app.route('/auth/callback')
def auth_callback():
    """Обрабатывает callback от Dodo IS."""
    code = request.args.get('code')
    user_id = request.args.get('state') #  state is used to send the user id
    user_data = get_user_data(int(user_id))
    if not user_data or not code :
        return "Ошибка авторизации: Неверный запрос.", 400
    code_verifier = user_data.get('code_verifier')
    access_token = get_access_token(int(user_id), code, code_verifier)
    if access_token:
        update_user_token(int(user_id), access_token)
        user_info = get_user_info(access_token)
        if user_info and "name" in user_info:
           update_user_name(int(user_id), user_info["name"])
           bot.send_message(int(user_id), f"Вы успешно авторизованы, {user_info['name']}!")
        else:
            bot.send_message(int(user_id), "Вы успешно авторизованы!")
        return "Authorization Successful, please type /start in bot to continue", 200
    else:
      return "Ошибка авторизации: Не удалось получить токен.", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True) # Port and host are just for testing.