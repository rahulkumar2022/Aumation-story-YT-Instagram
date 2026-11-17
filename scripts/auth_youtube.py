#!/usr/bin/env python3
"""
YouTube Data API v3 OAuth 2.0 Authorization Setup for Pass The Salt POV
-----------------------------------------------------------------------------
Generates a long-lived YOUTUBE_REFRESH_TOKEN so that GitHub Actions and local
scripts can automatically upload videos to YouTube without manual browser logins.
"""

import os
import sys
import json
import argparse
import urllib.parse
import urllib.request
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

REDIRECT_PORT = 8080
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"
SCOPES = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube"

def load_env_val(key):
    env_p = BASE_DIR / ".env"
    if env_p.exists():
        with open(env_p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip().strip("'\"")
    return os.environ.get(key, "")

DEFAULT_CLIENT_ID = load_env_val("YOUTUBE_CLIENT_ID")
DEFAULT_CLIENT_SECRET = load_env_val("YOUTUBE_CLIENT_SECRET")

captured_code = None
auth_error = None

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        global captured_code, auth_error
        parsed_url = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed_url.query)
        if "code" in query:
            captured_code = query["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <html>
            <body style="font-family: -apple-system, sans-serif; text-align: center; padding: 50px; background: #0f172a; color: #f8fafc;">
                <div style="max-width: 500px; margin: auto; padding: 30px; border-radius: 12px; background: #1e293b; border: 1px solid #334155;">
                    <h1 style="color: #22c55e;">✅ Channel Authorized!</h1>
                    <p style="color: #94a3b8; font-size: 16px;">Authorization code captured successfully for <strong>Pass The Salt POV</strong>.</p>
                    <p style="color: #cbd5e1;">You can close this window and return to your terminal.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode("utf-8"))
        elif "error" in query:
            auth_error = query["error"][0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"<h1>Authorization Failed: {auth_error}</h1>".encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def update_env_file(client_id: str, client_secret: str, refresh_token: str):
    env_path = BASE_DIR / ".env"
    lines = []
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

    keys_to_set = {
        "YOUTUBE_CLIENT_ID": client_id,
        "YOUTUBE_CLIENT_SECRET": client_secret,
        "YOUTUBE_REFRESH_TOKEN": refresh_token,
        "YOUTUBE_PRIVACY_STATUS": "public",
    }

    new_lines = []
    seen = set()
    for line in lines:
        matched = False
        for k in keys_to_set:
            if line.startswith(f"{k}="):
                new_lines.append(f'{k}="{keys_to_set[k]}"\n')
                seen.add(k)
                matched = True
                break
        if not matched:
            new_lines.append(line)

    for k, v in keys_to_set.items():
        if k not in seen:
            new_lines.append(f'{k}="{v}"\n')

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

def exchange_code_for_tokens(code: str, client_id: str, client_secret: str, redirect_uri: str) -> str:
    token_url = "https://oauth2.googleapis.com/token"
    token_data = urllib.parse.urlencode({
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }).encode("utf-8")

    req = urllib.request.Request(token_url, data=token_data, headers={"Content-Type": "application/x-www-form-urlencoded"})

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            tokens = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"\n❌ Token exchange failed (HTTP {e.code}): {e.read().decode('utf-8')}")
        sys.exit(1)

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        print("\n⚠️ Google did not return a refresh token.")
        print("   If you have already approved this app previously, visit:")
        print("   https://myaccount.google.com/permissions")
        print("   Remove access for this app, then re-run to get a fresh refresh token.")
        sys.exit(1)

    return refresh_token

def print_success_banner(client_id: str, client_secret: str, refresh_token: str):
    env_path = BASE_DIR / ".env"
    openrouter_key = "sk-or-v1-..."
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("OPENROUTER_API_KEY="):
                    openrouter_key = line.split("=", 1)[1].strip().strip("'\"")

    print("\n" + "=" * 80)
    print("🎉 YOUTUBE OAUTH 2.0 SETUP COMPLETE FOR PASS THE SALT POV!")
    print("=" * 80)
    print("Add these 4 secrets to your GitHub Repository:")
    print("👉 Repo: https://github.com/rahulkumar2022/Aumation-story-YT-Instagram")
    print("👉 Path: Settings -> Secrets and variables -> Actions -> New repository secret\n")
    print(f"1. Name:  OPENROUTER_API_KEY\n   Value: {openrouter_key}\n")
    print(f"2. Name:  YOUTUBE_CLIENT_ID\n   Value: {client_id}\n")
    print(f"3. Name:  YOUTUBE_CLIENT_SECRET\n   Value: {client_secret}\n")
    print(f"4. Name:  YOUTUBE_REFRESH_TOKEN\n   Value: {refresh_token}\n")
    print("=" * 80)
    print("Once added, every scheduled run or manual workflow dispatch will upload directly")
    print("to your YouTube channel as a public YouTube Short or Long-Form Episode!")
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="YouTube OAuth 2.0 Setup for Pass The Salt POV")
    parser.add_argument("--code", type=str, default=None, help="Authorization code if captured manually")
    parser.add_argument("--url", type=str, default=None, help="Full callback URL (e.g. http://localhost:8080/?code=...)")
    args = parser.parse_args()

    client_id = os.getenv("YOUTUBE_CLIENT_ID", DEFAULT_CLIENT_ID)
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", DEFAULT_CLIENT_SECRET)

    code_to_exchange = args.code
    if not code_to_exchange and args.url:
        parsed = urllib.parse.urlparse(args.url)
        q = urllib.parse.parse_qs(parsed.query)
        if "code" in q:
            code_to_exchange = q["code"][0]

    if code_to_exchange:
        print(f"🔄 Exchanging code for refresh token...")
        refresh_token = exchange_code_for_tokens(code_to_exchange, client_id, client_secret, REDIRECT_URI)
        update_env_file(client_id, client_secret, refresh_token)
        print("💾 Updated local .env file!")
        print_success_banner(client_id, client_secret, refresh_token)
        return

    # Interactive Browser Mode
    auth_params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(auth_params)}"

    print("=" * 80)
    print("🎬 YOUTUBE DATA API V3 OAUTH 2.0 SETUP")
    print("Channel: Pass The Salt POV")
    print("=" * 80)
    print(f"\n🌐 Starting temporary local receiver on {REDIRECT_URI} ...")

    try:
        server = HTTPServer(("127.0.0.1", REDIRECT_PORT), OAuthCallbackHandler)
    except OSError:
        server = HTTPServer(("localhost", REDIRECT_PORT), OAuthCallbackHandler)

    print(f"\n👉 Opening your browser to authorize channel:\n   {auth_url}\n")
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    print("⏳ Waiting for browser authorization callback...")
    global captured_code, auth_error
    while captured_code is None and auth_error is None:
        server.handle_request()

    if auth_error:
        print(f"\n❌ Authorization rejected by user: {auth_error}")
        sys.exit(1)

    print("\n✅ Authorization code received from Google!")
    print("🔄 Exchanging code for permanent YOUTUBE_REFRESH_TOKEN...")
    refresh_token = exchange_code_for_tokens(captured_code, client_id, client_secret, REDIRECT_URI)
    update_env_file(client_id, client_secret, refresh_token)
    print("💾 Updated local .env file!")
    print_success_banner(client_id, client_secret, refresh_token)

if __name__ == "__main__":
    main()
