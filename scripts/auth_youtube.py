#!/usr/bin/env python3
"""
Interactive YouTube OAuth Setup Helper.
Generates YOUTUBE_REFRESH_TOKEN for automated video publishing.
"""

import os
import sys
import json
import urllib.parse
import urllib.request
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, ".env")

# Scopes required for video uploads & metadata management
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

auth_code = None

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed_url = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_url.query)

        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html = """
            <html>
            <body style="font-family: sans-serif; text-align: center; padding: 50px; background: #0f172a; color: white;">
                <h1 style="color: #22c55e;">🎉 Authorization Successful!</h1>
                <p>Your YouTube authorization code has been received.</p>
                <p>You can close this tab and return to your terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed or denied.")

    def log_message(self, format, *args):
        return  # Silence server logs

def get_env_var(name):
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{name}="):
                    return line.split("=", 1)[1].strip().strip("'\"")
    return os.environ.get(name)

def save_env_var(name, value):
    lines = []
    found = False
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.strip().startswith(f"{name}="):
            new_lines.append(f"{name}={value}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{name}={value}\n")

    with open(ENV_FILE, "w") as f:
        f.writelines(new_lines)

def main():
    global auth_code
    print("=" * 65)
    print("🎬 YOUTUBE OAUTH CREDENTIAL GENERATOR FOR PASS THE SALT POV")
    print("=" * 65)

    client_id = get_env_var("YOUTUBE_CLIENT_ID")
    client_secret = get_env_var("YOUTUBE_CLIENT_SECRET")

    if not client_id:
        print("\n👉 Enter your Google Cloud OAuth Client ID:")
        client_id = input("Client ID: ").strip()
        save_env_var("YOUTUBE_CLIENT_ID", client_id)

    if not client_secret:
        print("\n👉 Enter your Google Cloud OAuth Client Secret:")
        client_secret = input("Client Secret: ").strip()
        save_env_var("YOUTUBE_CLIENT_SECRET", client_secret)

    redirect_uri = "http://localhost:8080"
    scope_str = " ".join(SCOPES)

    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urllib.parse.urlencode({
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scope_str,
            "access_type": "offline",
            "prompt": "consent"
        })
    )

    print("\n🌐 Opening Google Authorization in your web browser...")
    print("If it does not open automatically, copy & paste this link:")
    print(f"\n{auth_url}\n")

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    # Start local HTTP server to capture callback code
    print("⏳ Waiting for authorization on http://localhost:8080...")
    server = HTTPServer(("localhost", 8080), OAuthCallbackHandler)
    server.timeout = 180  # 3 minutes

    while not auth_code:
        server.handle_request()

    print("✅ Authorization code received from Google!")

    # Exchange authorization code for refresh token
    token_url = "https://oauth2.googleapis.com/token"
    token_data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=token_data, headers={"Content-Type": "application/x-www-form-urlencoded"})

    try:
        with urllib.request.urlopen(req) as resp:
            tokens = json.loads(resp.read().decode("utf-8"))
            refresh_token = tokens.get("refresh_token")

            if not refresh_token:
                print("⚠️ No refresh token returned. (Tip: Re-run with prompt=consent if already authorized).")
                print("Response:", tokens)
                return

            save_env_var("YOUTUBE_REFRESH_TOKEN", refresh_token)
            print("\n" + "=" * 65)
            print("🎉 SUCCESS! YOUTUBE REFRESH TOKEN GENERATED!")
            print("=" * 65)
            print(f"YOUTUBE_REFRESH_TOKEN={refresh_token}")
            print("\nSaved directly into your local .env file!")
            print("\n📋 GITHUB REPOSITORY SECRETS TO ADD:")
            print("Go to: https://github.com/rahulkumar2022/Aumation-story-YT-Instagram/settings/secrets/actions")
            print("Add the following 4 secrets:")
            print(f"1. OPENROUTER_API_KEY      = {get_env_var('OPENROUTER_API_KEY')}")
            print(f"2. YOUTUBE_CLIENT_ID       = {client_id}")
            print(f"3. YOUTUBE_CLIENT_SECRET   = {client_secret}")
            print(f"4. YOUTUBE_REFRESH_TOKEN   = {refresh_token}")
            print("=" * 65)

    except urllib.error.HTTPError as e:
        print(f"❌ Failed to exchange code for token: {e.code} - {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
