#!/usr/bin/env python3
"""
Automated Video Pipeline for Quiet Capital Style Videos.
Supports:
  - OpenRouter API (Claude 3.5, DeepSeek V3, GPT-4o, Gemini 2.0) for dynamic scriptwriting
  - Edge-TTS for Natural Neural Narration
  - Multi-track Emotional Background Score & SFX
  - Remotion Programmatic 9:16 Shorts (30-60s) & 16:9 Long Episodes (8-20m)
  - Publishing Queue for GitHub Actions
"""

import argparse
import asyncio
import datetime
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
import seo_keywords

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_VIDEO_DIR = os.path.join(BASE_DIR, "sample-video")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
QUEUE_FILE = os.path.join(OUTPUT_DIR, "publishing_queue.json")

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

# Ensure directories
os.makedirs(os.path.join(OUTPUT_DIR, "shorts"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "long"), exist_ok=True)

# --------------------------------------------------------------------------
# OPENROUTER DYNAMIC SCRIPT ENGINE
# --------------------------------------------------------------------------

def generate_story_with_openrouter(mode: str, target_minutes: int = 10, model: str = None) -> dict:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("ℹ️ No OPENROUTER_API_KEY detected in environment or .env file.")
        print("💡 To use dynamic AI scriptwriting, set OPENROUTER_API_KEY in your .env or shell.")
        print("Using curated high-retention story template as fallback.")
        return get_short_story() if mode == "short" else get_long_story(target_minutes)

    selected_model = model or os.environ.get("OPENROUTER_MODEL", "anthropic/claude-haiku-5.5")
    print(f"🤖 Calling OpenRouter API (Model: {selected_model}) for dynamic {mode.upper()} script...")

    if mode == "short":
        prompt = (
            "Write a viral 30 to 50 second second-person POV storytelling script in the style of the 'Quiet Capital' YouTube channel. "
            "Theme: Subtle stealth wealth, billionaire in disguise, toxic family dinner arrogance, or corporate karma where an arrogant person gets humbled by the quiet protagonist. "
            "Incorporate high-ranking YouTube search terms: 'pov stories', 'billionaire pov', 'animated stories', 'motion comic', 'billionaire in disguise', 'pass the salt pov', 'rich vs poor'. "
            "Format: Return ONLY a valid JSON object with keys: "
            "'title' (high CTR YouTube title starting with 'POV:' using formulas like 'POV: The Waiter Is Actually The Billionaire Owner (Motion Comic)' or 'POV: When Your Toxic Family Realizes Who You Are'), "
            "'description' (engaging 2-sentence synopsis focusing on karma, billionaire in disguise, and stealth wealth), "
            "'tags' (array of 6-8 tags like 'pov stories', 'billionaire pov', 'animated stories', 'motion comic', 'rich vs poor'), "
            "'script' (the exact spoken narration text, approximately 90 to 130 words), "
            "'image_prompts' (array of exactly 3 visual scene descriptions for motion comic panels: 1. opening dinner scene, 2. tense phone call scene, 3. plot twist reveal scene)."
        )
    else:
        target_words = max(1100, target_minutes * 145)
        prompt = (
            f"Write a gripping, multi-chapter long-form second-person POV storytelling script targeted for {target_minutes} minutes "
            f"(approximately {target_words} words spoken narration) in the style of the 'Quiet Capital' YouTube channel. "
            "Theme: A quiet, underestimated protagonist who secretly achieved massive financial/corporate success (billionaire heir / stealth wealth owner), "
            "contrasted with boastful relatives or colleagues, culminating in a satisfying, quiet checkmate twist. "
            "Incorporate high-ranking YouTube search terms: 'pov stories', 'billionaire pov', 'animated stories', 'motion comic', 'billionaire family pov', 'pass the salt pov', 'from poverty to billionaire'. "
            "Format: Return ONLY a valid JSON object with keys: "
            "'title' (dramatic high-CTR YouTube title starting with 'POV:' e.g. 'POV: You Belong To A Billionaire Family... But They Forgot You Own The Company'), "
            "'description' (gripping 2-3 sentence summary detailing the stealth wealth plot and family drama), "
            "'tags' (array of 8 search tags like 'pov stories', 'billionaire pov', 'animated stories', 'motion comic', 'stealth wealth', 'full story'), "
            "'script' (the complete narration, broken into 5-6 acts, vivid storytelling dialogue), "
            "'image_prompts' (array of exactly 5 visual scene descriptions for widescreen panels across the 5 acts)."
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/kids-animation",
        "X-Title": "Automated POV Video Pipeline",
        "Content-Type": "application/json"
    }

    payload = {
        "model": selected_model,
        "messages": [
            {"role": "system", "content": "You are an elite YouTube storytelling scriptwriter specializing in viral POV parables about quiet wealth and subtle karma. Always return valid JSON only with no markdown wrapping."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_text = data["choices"][0]["message"]["content"].strip()
            import re
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if json_match:
                story = json.loads(json_match.group(0))
            else:
                story = json.loads(raw_text)
            print(f"✨ Successfully generated new story: '{story.get('title')}'")
            return story
    except Exception as e:
        print(f"⚠️ OpenRouter generation failed ({e}). Falling back to local template.")
        return get_short_story() if mode == "short" else get_long_story(target_minutes)

# --------------------------------------------------------------------------
# FALLBACK STORY TEMPLATES
# --------------------------------------------------------------------------

def get_short_story():
    return {
        "title": "POV: Your brother brags at dinner... not knowing you own the building",
        "description": "Never brag before you know who signs the lease. Toxic family arrogance meets the ultimate billionaire checkmate. #pov #povstories #billionairepov #motioncomic #animatedstories #storytime #shorts",
        "tags": [
            "pov stories",
            "billionaire pov",
            "animated stories",
            "motion comic",
            "billionaire in disguise",
            "pass the salt pov",
            "rich vs poor",
            "shorts"
        ],
        "script": (
            "POV: Every family dinner, your older brother Marcus makes sure everyone knows he is the golden child. "
            "Tonight, he stands up at the table, waving an approval letter for a four-thousand-dollar luxury penthouse downtown. "
            "He puts the property manager on speakerphone so the entire room can hear his congratulations. "
            "The family leans in with pride. But then the manager hesitates: "
            "'Sorry sir, there is a hold on your file. The building owner just personally reviewed and rejected your lease.' "
            "Marcus turns pale in disbelief, stammering into the phone. "
            "Across the table, your phone buzzes with one notification: 'Tenant Application Rejected, Chairman.' "
            "You calmly take a sip of your coffee, look him in the eye... and ask him to pass the salt."
        )
    }

def get_long_story(target_minutes: int = 10):
    chapters = [
        "Chapter 1: The Sunday Ritual.\n"
        "Every single Sunday at exactly five-thirty in the afternoon, the low rumble of a tuned exhaust rolls down Oakridge Lane. "
        "It is your older brother Marcus, arriving in his brand-new leased Mercedes-Benz AMG. "
        "He never just parks. He circles the driveway twice, kills the engine with a flourish, and steps out adjusting his rose-gold watch so the neighbors can see the dial catch the late afternoon sun. "
        "Inside the house, your mother rushes to open the front door with a beaming smile, wiping her hands on her apron like royalty has arrived. "
        "And on the front porch steps, sitting in a faded hoodie with a warm ceramic mug of black coffee, you watch the entire spectacle unfold in absolute silence. "
        "Marcus glances in your direction, shakes his head with that practiced, condescending grin: 'Still in the same sweater from college, little brother? You know, the job market isn't that scary if you actually try.'",

        "Chapter 2: The Living Room Interrogation.\n"
        "Dinner at the household has never been about eating. It has always been about Marcus's quarterly performance review. "
        "He unbuttons his designer jacket, takes his seat at the head of the table next to Dad, and immediately props his company-issued iPhone against the salt shaker. "
        "For forty-five minutes, between mouthfuls of pot roast, the family is treated to a masterclass in corporate bragging. "
        "He casually mentions that the regional board is preparing to name him Senior Vice President of Field Operations before his thirty-fifth birthday. "
        "Then, as predictable as the tide, your father turns his gaze across the table toward you: "
        "'And what about you, son? Are you still doing those freelance computer things in your bedroom? A man needs a pension. Look at your brother.'",

        "Chapter 3: The Mailroom Offer.\n"
        "Marcus wipes his mouth with a linen napkin, reaches into his leather breast pocket, and pulls out a heavy, textured business card. "
        "Gold foil lettering: Apex Logistics Holdings — Senior Regional Director. "
        "'Tell you what,' Marcus says, his voice dripping with generous sympathy. "
        "'I have lunch with our executive director on Tuesday. I know you don't have much of a resume, but our central distribution facility is looking for mailroom sorters. It pays eighteen dollars an hour.' "
        "You look down at the card. You look at Marcus's self-satisfied smirk. "
        "You take another sip of coffee and quietly slide the card back toward him. 'Thanks Marcus. But I think I'm comfortable where I am.'",

        "Chapter 4: The Apex Annual Gala.\n"
        "Two weeks pass, and the annual Apex National Gala arrives in the grand ballroom of the St. Regis downtown. "
        "Tonight, the private equity group that secretly bought Apex two months ago is officially revealing their new Board Chairman. "
        "Marcus has convinced himself that this is his moment. He bought an Italian tuxedo. "
        "As they walk into the crystal-lit ballroom, your father is practically floating with pride. "
        "Marcus points out the VIP tables near the stage: 'See that private table with the gold reserved plaque? That is for the Chairman. Tonight, I introduce myself to the man who owns this empire.'",

        "Chapter 5: The Chairman's Arrival.\n"
        "At eight o'clock sharp, the chimes ring through the grand hall. "
        "The master of ceremonies steps to the podium: 'Ladies and gentlemen, tonight it is our distinct honor to welcome the principal owner, majority shareholder, and newly appointed Chairman of Apex Holdings.' "
        "Marcus straightens his bow tie, leans over to Dad, and whispers: 'Watch this. I'm going to be the first one to shake his hand.' "
        "The double oak doors swing open. Two security escorts step forward, flanking a single figure walking calmly down the center carpet. "
        "He is wearing a tailored charcoal suit with an open collar, hands casually in his pockets.",

        "Chapter 6: Checkmate.\n"
        "Marcus's jaw goes slack. His champagne glass tilts, spilling Dom Pérignon across his silk lapel. "
        "Your mother gasps, her hand flying to her throat. Your father stands frozen, his eyes bulging in pure disbelief. "
        "Walking past their table, without a hint of arrogance, is you. "
        "The CEO of Apex Logistics rushes over, bowing his head respectfully: 'Good evening, Chairman. The board is ready whenever you are.' "
        "You pause beside table number four. You meet Marcus's terrified eyes with a calm, warm smile. "
        "'Good to see you, Marcus,' you say quietly. 'I reviewed your regional department's audit this morning.' "
        "You tap his shoulder gently. 'Don't worry. Your job is safe... as long as you pass the salt.'"
    ]

    return {
        "title": "POV: You Belong To A Billionaire Family... But They Forgot You Own The Company",
        "description": "For seven years, your toxic family treated you like an unemployed failure while Marcus flexed his title. Until the annual Apex Gala. #pov #povstories #billionairepov #motioncomic #animatedstories #storytime #fullstory",
        "tags": [
            "pov stories",
            "billionaire pov",
            "animated stories",
            "motion comic",
            "billionaire family pov",
            "stealth wealth",
            "pass the salt pov",
            "corporate karma",
            "full story"
        ],
        "script": "\n\n".join(chapters)
    }

# --------------------------------------------------------------------------
# AUDIO SYNTHESIS & SCENE SCORING
# --------------------------------------------------------------------------

async def synthesize_voice(text: str, output_path: str):
    import edge_tts
    print(f"🎙️  Synthesizing neural voice with ChristopherNeural...")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    c = edge_tts.Communicate(text, "en-US-ChristopherNeural", rate="+2%", pitch="-1Hz")
    raw_path = output_path + ".raw.mp3"
    await c.save(raw_path)

    print(f"🎧  Adding cinematic ambient sub-bass underscore...")
    cmd = [
        "ffmpeg", "-y", "-i", raw_path,
        "-f", "lavfi", "-i", "sine=frequency=62:duration=1500",
        "-filter_complex", "[1:a]volume=0.025,lowpass=f=160[drone];[0:a][drone]amix=inputs=2:duration=first[a]",
        "-map", "[a]", output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if os.path.exists(raw_path):
        os.remove(raw_path)

def get_audio_duration_seconds(audio_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

# --------------------------------------------------------------------------
# REMOTION VIDEO RENDERING
# --------------------------------------------------------------------------

def render_remotion(composition_id: str, out_file: str, duration_in_frames: int):
    print(f"🎬  Rendering Remotion composition '{composition_id}' ({duration_in_frames} frames)...")
    cmd = [
        "npx", "remotion", "render",
        composition_id,
        out_file,
        f"--props={json.dumps({'durationInFrames': duration_in_frames})}"
    ]
    res = subprocess.run(cmd, cwd=SAMPLE_VIDEO_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print("❌ Remotion Render Error (stdout):", res.stdout[-800:])
        print("❌ Remotion Render Error (stderr):", res.stderr[-800:])
        raise RuntimeError("Remotion render failed")
    print(f"✅  Render complete: {out_file}")

# --------------------------------------------------------------------------
# QUEUE MANAGEMENT
# --------------------------------------------------------------------------

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

def generate_visual_panels(story: dict, mode: str, image_model: str = None):
    """Generates visual scene panels using OpenRouter Unified Image API."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from generate_images import generate_image_with_openrouter
    except Exception as e:
        print(f"⚠️ Could not load image generator module: {e}")
        return

    prompts = story.get("image_prompts", [])
    if not prompts:
        return

    print(f"\n🎨 Generating {len(prompts)} visual scenes via OpenRouter Image API...")
    if mode == "short":
        targets = [
            os.path.join(SAMPLE_VIDEO_DIR, "public", "short_p1.jpg"),
            os.path.join(SAMPLE_VIDEO_DIR, "public", "short_p2.jpg"),
            os.path.join(SAMPLE_VIDEO_DIR, "public", "short_p3.jpg"),
        ]
        ratio = "9:16"
    else:
        targets = [
            os.path.join(SAMPLE_VIDEO_DIR, "public", f"long_s{i+1}.jpg")
            for i in range(min(5, len(prompts)))
        ]
        ratio = "16:9"

    for i, target_path in enumerate(targets):
        if i < len(prompts):
            print(f"🖼️  Scene {i+1}/{len(targets)}...")
            generate_image_with_openrouter(prompts[i], target_path, aspect_ratio=ratio, model=image_model)

def run_pipeline(mode: str, duration_minutes: int = 10, model: str = None, generate_images: bool = True, image_model: str = None):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print("=" * 65)
    print(f"🚀 RUNNING AUTOMATED VIDEO PIPELINE: {mode.upper()}")
    print("=" * 65)

    # Step 1: Dynamic Story Generation (OpenRouter or Fallback)
    story = generate_story_with_openrouter(mode, duration_minutes, model=model)

    # Step 2: Dynamic Scene Image Generation via OpenRouter Image API (Default: True if API key present)
    has_api_key = bool(os.environ.get("OPENROUTER_API_KEY"))
    if generate_images and has_api_key:
        generate_visual_panels(story, mode, image_model=image_model)
    elif not has_api_key:
        print("ℹ️ Skipping dynamic image generation (no OPENROUTER_API_KEY). Using cached scene artwork.")

    if mode == "short":
        out_filename = f"short_{timestamp}.mp4"
        out_path = os.path.join(OUTPUT_DIR, "shorts", out_filename)
        audio_target = os.path.join(SAMPLE_VIDEO_DIR, "public", "short_narration.mp3")
        composition_id = "DedicatedShort"
    else:
        out_filename = f"long_{timestamp}.mp4"
        out_path = os.path.join(OUTPUT_DIR, "long", out_filename)
        audio_target = os.path.join(SAMPLE_VIDEO_DIR, "public", "long_narration.mp3")
        composition_id = "FullEpisodeLong"

    # Step 2: Voice Synthesis
    asyncio.run(synthesize_voice(story["script"], audio_target))

    # Step 3: Compute Duration from Audio
    duration_secs = get_audio_duration_seconds(audio_target)
    duration_frames = int(duration_secs * 30)
    print(f"⏱️  Computed Audio Duration: {duration_secs:.1f}s ({duration_frames} frames)")

    # Step 4: Render Remotion Video
    render_remotion(composition_id, out_path, duration_frames)

    # Step 5: Enqueue for Publishing
    queue = load_queue()
    formatted_desc = seo_keywords.format_description(story.get("description", ""), is_short=(mode == "short"))
    enriched_tags = seo_keywords.enrich_tags(story.get("tags", []), mode=mode)
    entry = {
        "id": f"{mode}_{timestamp}",
        "type": mode,
        "title": story["title"],
        "description": formatted_desc,
        "tags": enriched_tags,
        "duration_seconds": round(duration_secs, 2),
        "file_path": out_path,
        "created_at": datetime.datetime.now().isoformat(),
        "status": "ready_to_post",
        "posted": False
    }
    queue.append(entry)
    save_queue(queue)

    print("\n" + "=" * 65)
    print(f"🎉 SUCCESS! {mode.upper()} Video Enqueued for Publishing!")
    print(f"📁 Video: {out_path} ({duration_secs:.1f}s)")
    print(f"📋 Queue File: {QUEUE_FILE}")
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Video Generator with OpenRouter & Remotion")
    parser.add_argument("--mode", choices=["short", "long"], required=True, help="Video mode (short=30-60s, long=8-20m)")
    parser.add_argument("--duration-minutes", type=int, default=10, help="Target duration in minutes for long mode (8-20)")
    parser.add_argument("--model", type=str, default=None, help="OpenRouter text model (e.g. deepseek/deepseek-chat, anthropic/claude-3.5-sonnet, openai/gpt-4o)")
    parser.add_argument("--generate-images", action="store_true", default=True, help="Generate custom scene illustration panels using OpenRouter Image API")
    parser.add_argument("--no-images", action="store_true", help="Skip generating new AI images and use cached scene artwork")
    parser.add_argument("--image-model", type=str, default=None, help="OpenRouter image model (e.g. recraft/recraft-v4.1-flash-v2, bytedance-seed/seedream-5-0-flash, black-forest-labs/flux.2-flex)")
    args = parser.parse_args()
    should_generate = False if args.no_images else True
    run_pipeline(
        args.mode,
        args.duration_minutes,
        model=args.model,
        generate_images=should_generate,
        image_model=args.image_model
    )
