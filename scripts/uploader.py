#!/usr/bin/env python3
"""
Automated Social Media / YouTube Publisher.
Designed to be executed by GitHub Actions or local CLI.
Scans output/publishing_queue.json, uploads unposted videos,
and updates their status with the public video URL.
"""

import os
import sys
import json
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_FILE = os.path.join(BASE_DIR, "output", "publishing_queue.json")

# Automatically load environment variables from .env if present
def load_dotenv(dotenv_path=None):
    if not dotenv_path:
        dotenv_path = os.path.join(BASE_DIR, ".env")
    if os.path.isfile(dotenv_path):
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v

load_dotenv()

def get_access_token():
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        return None

    url = "https://oauth2.googleapis.com/token"
    payload = json.dumps({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("access_token")
    except Exception as e:
        print(f"⚠️ Error obtaining YouTube access token: {e}")
        return None

def upload_to_youtube(video_path: str, title: str, description: str, tags: list, is_short: bool, access_token: str):
    print(f"📤 Uploading '{title}' to YouTube...")
    metadata = {
        "snippet": {
            "title": f"{title} #Shorts" if is_short and "#Shorts" not in title else title,
            "description": description,
            "tags": tags,
            "categoryId": "24" # Entertainment
        },
        "status": {
            "privacyStatus": os.environ.get("YOUTUBE_PRIVACY_STATUS", "public"),
            "selfDeclaredMadeForKids": False
        }
    }

    # Step 1: Initialize resumable upload
    init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
    req = urllib.request.Request(
        init_url,
        data=json.dumps(metadata).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Type": "video/mp4"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            upload_url = resp.headers.get("Location")
    except Exception as e:
        print(f"❌ Failed to initiate YouTube upload: {e}")
        return None

    # Step 2: Upload video binary
    file_size = os.path.getsize(video_path)
    with open(video_path, "rb") as f:
        video_data = f.read()

    upload_req = urllib.request.Request(
        upload_url,
        data=video_data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "video/mp4",
            "Content-Length": str(file_size)
        },
        method="PUT"
    )

    try:
        with urllib.request.urlopen(upload_req) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            video_id = res_data.get("id")
            print(f"🎉 Upload successful! Video ID: {video_id}")
            return f"https://youtu.be/{video_id}"
    except Exception as e:
        print(f"❌ Failed to transfer video binary: {e}")
        return None

def load_queue():
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_queue(queue):
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)

def process_queue():
    queue = load_queue()
    if not queue:
        print("ℹ️ No publishing_queue.json found. Nothing to post.")
        return 0

    pending = [item for item in queue if not item.get("posted", False)]
    if not pending:
        print("✅ All queued videos have already been posted.")
        return 0

    print(f"📋 Found {len(pending)} pending video(s) to publish.")
    access_token = get_access_token()

    if not access_token:
        print("⚠️ No YouTube OAuth credentials detected in environment.")
        print("   Required GitHub Secrets: YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN")
        print("   Simulating dry-run / queue verification mode.")

    updated_count = 0
    for item in pending:
        video_path = item.get("file_path")
        if not os.path.exists(video_path):
            print(f"⚠️ Video file missing on disk: {video_path}")
            continue

        is_short = (item.get("type") == "short")
        if access_token:
            url = upload_to_youtube(
                video_path=video_path,
                title=item.get("title", "POV Story"),
                description=item.get("description", ""),
                tags=item.get("tags", []),
                is_short=is_short,
                access_token=access_token
            )
            if url:
                item["posted"] = True
                item["status"] = "published"
                item["published_url"] = url
                updated_count += 1
        else:
            print(f"   [DRY RUN] Ready to publish: '{item.get('title')}' ({item.get('type')}) -> {video_path}")

    if updated_count > 0:
        save_queue(queue)
        print("💾 Updated publishing_queue.json with live publication links.")
    return updated_count

def main():
    process_queue()

if __name__ == "__main__":
    main()
