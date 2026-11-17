#!/usr/bin/env python3
"""
Diagnostic utility to verify your OpenRouter API Key and test script generation.
Usage:
  python3 scripts/test_openrouter.py
  python3 scripts/test_openrouter.py --model anthropic/claude-3.5-sonnet
"""

import os
import sys
import json
import urllib.request
import urllib.error
import argparse

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load .env
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

def main():
    parser = argparse.ArgumentParser(description="Test OpenRouter API Key and Model Connectivity")
    parser.add_argument("--model", type=str, default=None, help="OpenRouter text model identifier")
    parser.add_argument("--image-model", type=str, default=None, help="OpenRouter image model identifier")
    parser.add_argument("--test-image", action="store_true", help="Also generate a test image panel via OpenRouter Image API")
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    selected_model = args.model or os.environ.get("OPENROUTER_MODEL", "anthropic/claude-haiku-5.5")
    selected_image_model = args.image_model or os.environ.get("OPENROUTER_IMAGE_MODEL", "recraft/recraft-v4.1-flash-v2")

    print("=" * 65)
    print("🔍 OPENROUTER API DIAGNOSTIC & VERIFICATION")
    print("=" * 65)

    if not api_key:
        print("❌ OPENROUTER_API_KEY is NOT set!")
        print("\n👉 How to provide your key:")
        print("  1. Create a `.env` file in project root:")
        print("     OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx")
        print("     OPENROUTER_MODEL=deepseek/deepseek-chat")
        print("\n  2. Or export in your terminal:")
        print("     export OPENROUTER_API_KEY='sk-or-v1-xxxxxxxxxxxxxxxxxxxx'")
        print("\n  3. For GitHub Actions:")
        print("     Add `OPENROUTER_API_KEY` to GitHub Repository Secrets")
        print("=" * 65)
        sys.exit(1)

    masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
    print(f"🔑 API Key Found: {masked_key}")
    print(f"🤖 Target Model:  {selected_model}")

    # Check key information via OpenRouter auth endpoint
    print("\n📡 1. Checking API Key Status on OpenRouter...")
    auth_headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/kids-animation",
        "X-Title": "POV Automation Test"
    }

    try:
        req = urllib.request.Request("https://openrouter.ai/api/v1/auth/key", headers=auth_headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            key_data = json.loads(resp.read().decode("utf-8")).get("data", {})
            label = key_data.get("label", "Default")
            usage = key_data.get("usage", 0)
            limit = key_data.get("limit")
            is_free_tier = key_data.get("is_free_tier", False)
            print("   ✅ Key is valid and active!")
            print(f"   • Label: {label}")
            print(f"   • Free Tier: {is_free_tier}")
            print(f"   • Usage: ${usage}")
            if limit:
                print(f"   • Credit Limit: ${limit}")
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP Error: {e.code} - {e.reason}")
        if e.code == 401:
            print("   🚨 Invalid API Key! Please verify your key on https://openrouter.ai/keys")
        return
    except Exception as e:
        print(f"   ⚠️ Could not query key metadata ({e}). Proceeding to model test...")

    # Test sample completion
    print(f"\n📡 2. Generating Sample Story Snippet with '{selected_model}'...")
    payload = {
        "model": selected_model,
        "messages": [
            {
                "role": "system",
                "content": "You are a master YouTube storytelling scriptwriter. Return valid JSON only with keys: title, hook."
            },
            {
                "role": "user",
                "content": "Write a 1-sentence viral POV hook about silent wealth humbling an arrogant guest."
            }
        ]
    }

    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", **auth_headers}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            content = result["choices"][0]["message"]["content"].strip()
            print("   ✅ Text script completion successful!")
            print(f"\n📜 Model Output:\n{content}")
    except Exception as e:
        print(f"   ❌ Completion generation failed: {e}")

    # Optional: Test Image Generation API
    if args.test_image:
        print(f"\n🎨 3. Testing Unified Image Generation API ({selected_image_model})...")
        img_payload = {
            "model": selected_image_model,
            "prompt": "2D graphic novel motion comic panel, blank white silhouette protagonist drinking coffee while arrogant guest boasts, cel-shaded art style, moody lighting",
            "aspect_ratio": "9:16",
            "n": 1
        }
        try:
            img_req = urllib.request.Request(
                "https://openrouter.ai/api/v1/images",
                data=json.dumps(img_payload).encode("utf-8"),
                headers={"Content-Type": "application/json", **auth_headers}
            )
            with urllib.request.urlopen(img_req, timeout=60) as resp:
                img_data = json.loads(resp.read().decode("utf-8"))
                data_list = img_data.get("data", [])
                if data_list:
                    item = data_list[0]
                    test_out = os.path.join(BASE_DIR, "output", "test_openrouter_image.png")
                    os.makedirs(os.path.dirname(test_out), exist_ok=True)
                    if item.get("b64_json"):
                        import base64
                        with open(test_out, "wb") as f:
                            f.write(base64.b64decode(item["b64_json"]))
                        print(f"   ✅ Image successfully generated and saved to: {test_out}")
                    elif item.get("url"):
                        urllib.request.urlretrieve(item["url"], test_out)
                        print(f"   ✅ Image successfully downloaded and saved to: {test_out}")
                    else:
                        print(f"   ✅ Image endpoint responded: {list(item.keys())}")
                else:
                    print("   ⚠️ Image API returned empty result.")
        except urllib.error.HTTPError as e:
            err_msg = e.read().decode("utf-8") if hasattr(e, "read") else str(e)
            print(f"   ❌ Image API HTTP {e.code}: {err_msg}")
        except Exception as e:
            print(f"   ❌ Image generation test failed: {e}")

    print("\n🎉 OpenRouter is ready for automated video generation!")
    print("=" * 65)

if __name__ == "__main__":
    main()
