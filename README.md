# Automation-story-YT-Instagram

> Autonomous 2D Motion Comic Video Factory for YouTube Shorts & Long-Form Parables (inspired by *Quiet Capital*).

An automated end-to-end video production and publishing engine. It writes viral second-person POV scripts, generates 2D comic panels, synthesizes neural voiceover, composes emotional soundtrack and sound effects, and renders high-retention videos programmatically using **Remotion**, powered by **OpenRouter API** and automated via **GitHub Actions**.

---

## 🎬 Formats Produced

| Format | Aspect Ratio | Resolution | Target Duration | Schedule |
| :--- | :--- | :--- | :--- | :--- |
| **Shorts / Reels** | `9:16` vertical | `1080x1920` | **30 – 60 seconds** | **Every day** (`0 10 * * *`) |
| **Full Episodes** | `16:9` widescreen | `1920x1080` | **8 – 20 minutes** | **Every 4 days** (`0 14 */4 * *`) |

---

## ⚡ Tech Stack & Architecture

- **Story & Scriptwriting:** OpenRouter API (`anthropic/claude-haiku-5.5`, `deepseek/deepseek-chat`, `claude-3.5-sonnet`)
- **2D Visual Generation:** OpenRouter Unified Image API (`recraft/recraft-v4.1-flash-v2`, `flux.2-flex`)
- **Voice Synthesis:** Microsoft Natural Neural Voice (`en-US-ChristopherNeural` via Edge-TTS)
- **Render Engine:** [Remotion 4.0](https://www.remotion.dev/) (React 19 + TypeScript + Chromium)
- **Sound Design:** Dynamic multi-track score + procedural SFX (phone rings, tension sweeps, 808 sub drops)
- **CI/CD Automation:** GitHub Actions (`.github/workflows/generate_and_publish.yml`)
- **Publishing:** YouTube Data API v3 automatic resumable uploader

---

## 🚀 Quick Start

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/rahulkumar2022/Aumation-story-YT-Instagram.git
cd Aumation-story-YT-Instagram

# Install Remotion dependencies
cd sample-video && npm install && cd ..

# Install Python requirements
pip install edge-tts numpy scipy requests
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` and add your keys:
```ini
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxx
OPENROUTER_MODEL=anthropic/claude-haiku-5.5
OPENROUTER_IMAGE_MODEL=recraft/recraft-v4.1-flash-v2

# (Optional) YouTube API credentials for automated uploads
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=
YOUTUBE_REFRESH_TOKEN=
```

### 3. Verify OpenRouter Connectivity
```bash
# Test story and image generation in 2 seconds
python3 scripts/test_openrouter.py --test-image
```

### 4. Generate Videos Locally
```bash
# Generate a 30-60s YouTube Short with AI story & comic panels
python3 scripts/auto_pipeline.py --mode short

# Generate an 8-20m widescreen episode
python3 scripts/auto_pipeline.py --mode long --duration-minutes 8
```

---

## 🤖 GitHub Actions 24/7 Automation

This repository includes a turnkey GitHub Actions workflow (`.github/workflows/generate_and_publish.yml`) that runs on a schedule:
- **Daily at 10:00 AM UTC:** Automatically writes, synthesizes, renders, and publishes a Short.
- **Every 4 Days at 2:00 PM UTC:** Automatically writes, synthesizes, renders, and publishes a Long-Form episode.

### Setting up GitHub Secrets:
Add these in your repository at **Settings** → **Secrets and variables** → **Actions**:
1. `OPENROUTER_API_KEY`: Your OpenRouter API key.
2. `YOUTUBE_CLIENT_ID`: Google Cloud OAuth Client ID.
3. `YOUTUBE_CLIENT_SECRET`: Google Cloud OAuth Client Secret.
4. `YOUTUBE_REFRESH_TOKEN`: OAuth Refresh Token with YouTube upload permissions.

---

## 📁 Repository Structure

```
├── .github/workflows/
│   └── generate_and_publish.yml  # Turnkey GitHub Actions CI/CD cron
├── assets/                       # Curated character silhouettes & artwork
├── output/
│   ├── publishing_queue.json     # Tracking queue of generated videos
│   ├── shorts/                   # Rendered 9:16 Shorts MP4s
│   └── long/                     # Rendered 16:9 Episodes MP4s
├── sample-video/
│   ├── src/
│   │   ├── Composition.tsx       # Remotion React motion comic compositions
│   │   └── Root.tsx
│   └── public/                   # Audio narration, BGM, SFX & scene images
├── scripts/
│   ├── auto_pipeline.py          # Master generator (Story + Voice + Render)
│   ├── generate_images.py        # OpenRouter Unified Image API engine
│   ├── test_openrouter.py        # Diagnostic & verification utility
│   ├── uploader.py               # YouTube Data API v3 uploader
│   └── setup_cron.sh             # Local system crontab installer
├── .env.example                  # Environment configuration template
└── README.md
```

---

## 📜 License
MIT
