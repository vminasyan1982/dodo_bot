import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DODO_API_TOKEN = os.getenv("DODO_API_TOKEN")
DODO_API_URL = os.getenv("DODO_API_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = os.getenv("SCOPE")
PORT = 5001

if not BOT_TOKEN:
    print("Ошибка: токен Telegram бота не найден в файле .env")
    exit()

if not DODO_API_TOKEN or not DODO_API_URL:
    print("Ошибка: токен DODO API или URL не найдены в файле .env")
    exit()
if not CLIENT_ID or not CLIENT_SECRET:
    print("Ошибка: Client Id или Client Secret не найдены в файле .env")
    exit()
if not REDIRECT_URI:
    print("Ошибка: REDIRECT_URI не найден в файле .env")
    exit()
if not SCOPE:
    print("Ошибка: SCOPE не найден в файле .env")
    exit()
