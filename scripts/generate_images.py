#!/usr/bin/env python3
"""
OpenRouter Automated Image Generation for Quiet Capital Style Videos.
Uses OpenRouter's Unified Image API (POST https://openrouter.ai/api/v1/images).
Uses the SAME OPENROUTER_API_KEY used for scriptwriting!
"""

import os
import sys
import json
import base64
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Auto-load .env
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

# Quiet Capital aesthetic prompt prefix & style anchor
STYLE_ANCHOR = (
    "2D graphic novel motion comic panel, cel-shaded illustration, dark atmospheric moody lighting, "
    "clean vector linework, high contrast, blank white silhouette protagonist with no facial features, "
    "cinematic dramatic camera angle, Quiet Capital art style."
)

DEFAULT_IMAGE_MODEL = os.environ.get("OPENROUTER_IMAGE_MODEL", "recraft/recraft-v4.1-flash-v2")

def generate_image_with_openrouter(
    prompt: str,
    output_path: str,
    aspect_ratio: str = "9:16",
    model: str = None
) -> str:
    """
    Generates an image via OpenRouter's Image API and saves it to output_path.
    aspect_ratio: "9:16" for Shorts, "16:9" for Long Form episodes.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("ℹ️ No OPENROUTER_API_KEY set for image generation. Skipping dynamic image generation.")
        return None

    selected_model = model or DEFAULT_IMAGE_MODEL
    full_prompt = f"{prompt}, {STYLE_ANCHOR}"

    print(f"🎨 Generating Image via OpenRouter ({selected_model}) [{aspect_ratio}]...")
    print(f"   Prompt: {prompt[:90]}...")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/kids-animation",
        "X-Title": "Quiet Capital Image Pipeline",
        "Content-Type": "application/json"
    }

    payload = {
        "model": selected_model,
        "prompt": full_prompt,
        "aspect_ratio": aspect_ratio,
        "n": 1
    }

    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/images",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            data_arr = res_data.get("data", [])
            if not data_arr:
                print("⚠️ OpenRouter returned empty data array.")
                return None

            item = data_arr[0]
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            # Case 1: Base64 JSON
            if item.get("b64_json"):
                img_bytes = base64.b64decode(item["b64_json"])
                with open(output_path, "wb") as f:
                    f.write(img_bytes)
                print(f"✅ Image saved from Base64: {output_path}")
                return output_path

            # Case 2: URL
            elif item.get("url"):
                url = item["url"]
                urllib.request.urlretrieve(url, output_path)
                print(f"✅ Image downloaded from URL: {output_path}")
                return output_path
            else:
                print(f"⚠️ Unrecognized image data format: {item.keys()}")
                return None

    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8") if hasattr(e, "read") else str(e)
        print(f"❌ OpenRouter Image Generation HTTP Error {e.code}: {err_msg}")
        return None
    except Exception as e:
        print(f"❌ Error during image generation: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_prompt = sys.argv[1]
    else:
        test_prompt = "Family dinner scene where an arrogant brother boasts on speakerphone while the quiet protagonist listens"
    
    out_file = os.path.join(BASE_DIR, "output", "test_openrouter_image.png")
    res = generate_image_with_openrouter(test_prompt, out_file, aspect_ratio="9:16")
    if res:
        print(f"🎉 Success! Image generated at {res}")
    else:
        print("❌ Image generation test ended without output.")
