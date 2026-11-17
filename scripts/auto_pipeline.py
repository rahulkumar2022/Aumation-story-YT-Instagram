#!/usr/bin/env python3
"""
Automated Video Pipeline for Quiet Capital Style Videos.
Configurations:
  - Shorts / Reels: 30 to 60 seconds (Default: 45s, 9:16 vertical 1080x1920)
  - Long-Form Episodes: 8 to 20 minutes (Default: 10m, 16:9 widescreen 1920x1080)
Saves videos and metadata to output/publishing_queue.json for GitHub Actions posting.
"""

import argparse
import asyncio
import datetime
import json
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_VIDEO_DIR = os.path.join(BASE_DIR, "sample-video")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
QUEUE_FILE = os.path.join(OUTPUT_DIR, "publishing_queue.json")

# Ensure directories
os.makedirs(os.path.join(OUTPUT_DIR, "shorts"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "long"), exist_ok=True)

# --------------------------------------------------------------------------
# STORY SCRIPTS: 30-60s SHORTS & 8-20m LONG EPISODES
# --------------------------------------------------------------------------

def get_short_story():
    """Generates a 30 to 60 second viral POV story (~90-130 words)."""
    return {
        "title": "POV: Your brother brags at dinner... not knowing you own the building",
        "description": "Never brag before you know who signs the lease. Sibling rivalry meets the ultimate workplace plot twist. #pov #karma #storytime #quietwealth #shorts",
        "tags": ["pov", "storytime", "instantkarma", "quietwealth", "shorts", "reels"],
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
    """
    Generates a full 8 to 20 minute episodic narrative.
    Paced at ~140 words per minute with 6 distinct acts / chapters.
    """
    title = "POV: Your Family Calls You The Failure — Until Marcus Brings You To His Corporate Gala"
    description = (
        "For seven years, your family believed you were unemployed while your brother Marcus flexed his six-figure corporate title. "
        "Until the night of the annual Apex Holdings Gala, where every executive in the room stands up when you walk through the door. "
        "#pov #storytime #stealthwealth #drama #familytwist #karma"
    )
    tags = ["stealthwealth", "familydrama", "storytime", "quietwealth", "corporatekarma", "longform"]

    # Multi-chapter narrative breakdown (Act 1 to Act 6)
    chapters = [
        # Act 1: The Driveway Dynamic
        "Chapter 1: The Sunday Ritual.\n"
        "Every single Sunday at exactly five-thirty in the afternoon, the low rumble of a tuned exhaust rolls down Oakridge Lane. "
        "It is your older brother Marcus, arriving in his brand-new leased Mercedes-Benz AMG. "
        "He never just parks. He circles the driveway twice, kills the engine with a flourish, and steps out adjusting his rose-gold watch so the neighbors can see the dial catch the late afternoon sun. "
        "Inside the house, your mother rushes to open the front door with a beaming smile, wiping her hands on her apron like royalty has arrived. "
        "Your father drops his newspaper, ready to hear the latest corporate earnings report from his star child. "
        "And on the front porch steps, sitting in a faded hoodie with a warm ceramic mug of black coffee, you watch the entire spectacle unfold in absolute silence. "
        "Marcus glances in your direction, shakes his head with that practiced, condescending grin, and mutters loud enough for your father to hear: "
        "'Still in the same sweater from college, little brother? You know, the job market isn't that scary if you actually try.'",

        # Act 2: The Dinner Interrogation
        "Chapter 2: The Living Room Interrogation.\n"
        "Dinner at the household has never been about eating. It has always been about Marcus's quarterly performance review. "
        "He unbuttons his designer jacket, takes his seat at the head of the table next to Dad, and immediately props his company-issued iPhone against the salt shaker. "
        "For forty-five minutes, between mouthfuls of pot roast and steamed vegetables, the family is treated to a masterclass in corporate bragging. "
        "He talks about his flight upgrades. He talks about his twelve-thousand-dollar quarterly bonus. "
        "He casually mentions that the regional board is preparing to name him Senior Vice President of Field Operations before his thirty-fifth birthday. "
        "Your mother claps her hands together like a schoolgirl. 'Oh Marcus, we always knew you had the drive. You got that from your father's side.' "
        "Then, as predictable as the tide, your father turns his gaze across the mahogany table toward you. "
        "The smile fades into that familiar mixture of disappointment and tired pity. "
        "'And what about you, son? Are you still doing those freelance computer things in your bedroom? A man needs benefits. A man needs a pension. Look at your brother.'",

        # Act 3: The Mailroom Humiliation
        "Chapter 3: The Mailroom Offer.\n"
        "Marcus wipes his mouth with a linen napkin, reaches into his leather breast pocket, and pulls out a heavy, textured business card. "
        "He slides it across the polished wood until it rests against your coffee saucer. "
        "Gold foil lettering. Apex Logistics Holdings — Senior Regional Director. "
        "'Tell you what,' Marcus says, his voice dripping with generous sympathy. "
        "'I have lunch with our executive director on Tuesday. I know you don't have much of a resume, but our central distribution facility is looking for mailroom sorters. "
        "It pays eighteen dollars an hour, full healthcare, and if you keep your head down and don't cause trouble, in five years you might make junior dispatch.' "
        "Your mother nods vigorously. 'Take it, please. Marcus is sticking his neck out for you.' "
        "You look down at the card. You look at Marcus's self-satisfied smirk. "
        "You take another sip of coffee and quietly slide the card back toward him. 'Thanks Marcus. But I think I'm comfortable where I am.' "
        "Marcus laughs out loud, tossing his hands in the air. 'Unbelievable. Some people just want to stay at the bottom forever.'",

        # Act 4: The Gala Invitation & Rising Stakes
        "Chapter 4: The Apex Annual Gala.\n"
        "Two weeks pass, and the annual Apex National Gala arrives. "
        "The event is held in the grand ballroom of the St. Regis downtown — a black-tie gathering of the state's most powerful logistics barons, hedge fund partners, and corporate directors. "
        "Marcus has spent three months preparing his speech. Tonight, the private equity group that secretly bought Apex two months ago is officially revealing their new Board Chairman. "
        "Marcus has convinced himself that this is his moment. He bought an Italian tuxedo. He rented a limousine for Mom and Dad so they could sit at his assigned table and watch his ascension. "
        "As they walk into the crystal-lit ballroom, your father is practically floating with pride. "
        "Marcus points out the VIP tables near the stage: 'See that private table with the gold reserved plaque? That is for the Chairman and the majority shareholders. Tonight, I introduce myself to the man who owns this empire.'",

        # Act 5: The Chairman's Arrival
        "Chapter 5: The Silence in the Ballroom.\n"
        "At eight o'clock sharp, the chimes ring through the grand hall. "
        "The master of ceremonies steps to the podium and taps the microphone. The room of five hundred executives falls dead quiet. "
        "'Ladies and gentlemen, tonight marks a historic chapter in our company's fifty-year history. "
        "As you know, our sixty-million-dollar acquisition was finalized last week by Ridgeway Capital. "
        "Tonight, it is our distinct honor to welcome the principal owner, majority shareholder, and newly appointed Chairman of Apex Holdings.' "
        "Marcus straightens his bow tie, leans over to Dad, and whispers: 'Watch this. I'm going to be the first one to shake his hand.' "
        "The double oak doors at the back of the ballroom swing open. "
        "Two security escorts in dark suits step forward, flanking a single figure walking calmly down the center carpet toward the main stage. "
        "He isn't wearing a tuxedo. He is wearing a tailored charcoal suit with an open collar, hands casually in his pockets.",

        # Act 6: Checkmate
        "Chapter 6: Checkmate.\n"
        "Marcus's jaw goes slack. His champagne glass tilts, spilling Dom Pérignon across his silk lapel. "
        "Your mother gasps, her hand flying to her throat. Your father stands frozen in his chair, his eyes bulging in pure disbelief. "
        "Walking past their table, without a hint of arrogance, is you. "
        "The CEO of Apex Logistics rushes over, bowing his head respectfully: 'Good evening, Chairman. The board is ready whenever you are.' "
        "You pause beside table number four. You look at Marcus, whose face has drained of every drop of color. "
        "The sweat is running down his temples, his breath caught in his throat as the realization crushes the air out of his chest. "
        "You look down at his spilled champagne, then meet his terrified eyes with a calm, warm smile. "
        "'Good to see you, Marcus,' you say quietly. 'I reviewed your regional department's audit this morning.' "
        "You tap his shoulder gently. 'Don't worry. Your job is safe... as long as you pass the salt.'"
    ]

    full_script = "\n\n".join(chapters)
    return {
        "title": title,
        "description": description,
        "tags": tags,
        "script": full_script
    }

# --------------------------------------------------------------------------
# AUDIO SYNTHESIS & AMBIENT MIXING
# --------------------------------------------------------------------------

async def synthesize_voice(text: str, output_path: str):
    import edge_tts
    print(f"🎙️  Synthesizing neural voice with ChristopherNeural...")
    c = edge_tts.Communicate(text, "en-US-ChristopherNeural", rate="+2%", pitch="-1Hz")
    raw_path = output_path + ".raw.mp3"
    await c.save(raw_path)

    # Mix subtle ambient drone bed
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
        print("❌ Remotion Render Error:", res.stderr[-500:])
        raise RuntimeError("Remotion render failed")
    print(f"✅  Render complete: {out_file}")

# --------------------------------------------------------------------------
# QUEUE MANAGEMENT FOR GITHUB ACTIONS
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

def run_pipeline(mode: str, duration_minutes: int = 10):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print("=" * 65)
    print(f"🚀 RUNNING AUTOMATED VIDEO PIPELINE: {mode.upper()}")
    print("=" * 65)

    if mode == "short":
        # 30-60 Seconds Short
        story = get_short_story()
        out_filename = f"short_{timestamp}.mp4"
        out_path = os.path.join(OUTPUT_DIR, "shorts", out_filename)
        audio_target = os.path.join(SAMPLE_VIDEO_DIR, "public", "short_narration.mp3")
        composition_id = "DedicatedShort"
    else:
        # 8-20 Minutes Long-Form Video
        story = get_long_story(target_minutes=duration_minutes)
        out_filename = f"long_{timestamp}.mp4"
        out_path = os.path.join(OUTPUT_DIR, "long", out_filename)
        audio_target = os.path.join(SAMPLE_VIDEO_DIR, "public", "long_narration.mp3")
        composition_id = "FullEpisodeLong"

    # Step 1: Voice Synthesis
    asyncio.run(synthesize_voice(story["script"], audio_target))

    # Step 2: Compute Duration from Audio
    duration_secs = get_audio_duration_seconds(audio_target)
    duration_frames = int(duration_secs * 30)
    print(f"⏱️  Computed Audio Duration: {duration_secs:.1f}s ({duration_frames} frames)")

    # Step 3: Render Remotion Video
    render_remotion(composition_id, out_path, duration_frames)

    # Step 4: Register in Publishing Queue for GitHub Actions
    queue = load_queue()
    entry = {
        "id": f"{mode}_{timestamp}",
        "type": mode,
        "title": story["title"],
        "description": story["description"],
        "tags": story["tags"],
        "duration_seconds": round(duration_secs, 2),
        "file_path": out_path,
        "created_at": datetime.datetime.now().isoformat(),
        "status": "ready_to_post",
        "posted": False
    }
    queue.append(entry)
    save_queue(queue)

    print("\n" + "=" * 65)
    print(f"🎉 SUCCESS! {mode.upper()} Video Enqueued for GHA Posting!")
    print(f"📁 Video: {out_path} ({duration_secs:.1f}s)")
    print(f"📋 Queue File: {QUEUE_FILE}")
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Video Generator & GHA Publisher")
    parser.add_argument("--mode", choices=["short", "long"], required=True, help="Video mode (short=30-60s, long=8-20m)")
    parser.add_argument("--duration-minutes", type=int, default=10, help="Target duration in minutes for long mode (8-20)")
    args = parser.parse_args()
    run_pipeline(args.mode, args.duration_minutes)
