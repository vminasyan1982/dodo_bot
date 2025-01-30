import http.server
import socketserver
import ssl
import os
import requests
import webbrowser
import base64
import hashlib
import secrets
import json
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

# Define variables
PORT = 5001
REDIRECT_URI = os.getenv("REDIRECT_URI")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SCOPE = os.getenv("SCOPE")


# Function to generate code verifier and challenge
def generate_pkce_codes():
    code_verifier = secrets.token_urlsafe(100)
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode('utf-8').replace(
        '=', '')
    return code_verifier, code_challenge


# Generate PKCE codes
code_verifier, code_challenge = generate_pkce_codes()


# Define handler for redirect URL
class MyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(
            b"<html><head><title>Authorization Successful</title></head><body><h1>Authorization Successful!</h1><p>You can close this tab.</p></body></html>")

        query_components = parse_qs(urlparse(self.path).query)
        code = query_components.get('code', [''])[0]

        if code:
            # Exchange code for access token
            token_url = "https://login.dodois.com/connect/token"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
                "code": code,
                "code_verifier": code_verifier
            }
            response = requests.post(token_url, headers=headers, data=data)

            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                if access_token:
                    print(f"Access Token: {access_token}")
                else:
                    print(f"Error getting access token {response.json()}")
            else:
                print(f"Error getting token {response.status_code}: {response.text}")
        else:
            print(f"Authorization code not found")
        self.server.shutdown()


# Generate authorization URL
auth_url = (
    f"https://auth.dodois.io/connect/authorize"
    f"?client_id={CLIENT_ID}"
    f"&scope={SCOPE}"
    f"&response_type=code"
    f"&redirect_uri={REDIRECT_URI}"
    f"&code_challenge={code_challenge}"
    f"&code_challenge_method=S256"
)

print("Open this link in browser:")
print(auth_url)

# Create server instance
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    httpd.timeout = 100
    # Open browser to authorization URL
    webbrowser.open(auth_url)
    httpd.handle_request()