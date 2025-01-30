import requests
from config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
import logging
import base64

logging.basicConfig(level=logging.DEBUG)


def get_access_token(user_id, code, code_verifier):
    token_url = "https://auth.dodois.io/connect/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "code_verifier": code_verifier
    }
    try:
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        return response.json().get('access_token')
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при получении токена доступа: {e}")
        return None