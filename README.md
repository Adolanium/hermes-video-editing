# Hermes Video Editing Skill

A comprehensive video editing toolkit for [Hermes Agent](https://github.com/nousresearch/hermes-agent) — edit videos by describing what you want in natural language.

Built entirely on free, open-source tools. No paid subscriptions required.

## Features

### Core Editing (Free, Local)
- **Trim & cut** — Remove sections by timestamp
- **Concatenate** — Join multiple clips
- **Speed change** — Speed up or slow down footage
- **Audio mixing** — Add music beds, replace audio, normalise levels
- **Text overlays** — Burn titles, lower-thirds, watermarks
- **Platform export** — One-command export for Instagram, YouTube, TikTok, Twitter, Telegram

### AI-Powered (Free, Local)
- **Auto-captioning** — Whisper transcription with subtitle burn-in
- **Silence removal** — Detect and cut silent sections (Silero VAD + ffmpeg fallback)
- **Scene detection** — Automatically find cuts and scene changes (PySceneDetect)
- **Smart reframing** — Face-tracking crop for different aspect ratios (OpenCV)
- **Stabilisation** — Fix shaky footage (ffmpeg vidstab)
- **Background removal** — AI-powered background removal from video
- **Colour enhancement** — Auto brightness, contrast, and denoise

### Visual Review
- **Frame extraction** — Sample frames at intervals for quality control
- **Thumbnail grid** — Generate contact sheets for at-a-glance review
- **AI vision inspection** — Integration with Hermes vision tools to verify edits

### Cloud APIs (Optional, Paid)
- **Runway ML** — Generative video, style transfer, B-roll generation
- **Shotstack** — Cloud rendering, template-driven production

## Installation

### Quick Start

```bash
# Install dependencies
bash install.sh

# Or core only (no AI tools)
bash install.sh --core

# Check what's installed
bash install.sh --check
```

### Manual Install

```bash
# System dependency
sudo apt-get install ffmpeg

# Core Python packages
pip install moviepy ffmpeg-python opencv-python-headless Pillow numpy

# Optional AI tools
pip install openai-whisper          # Transcription
pip install scenedetect[opencv]     # Scene detection
pip install torch                   # Silero VAD
pip install backgroundremover       # Background removal
```

### As a Hermes Skill

Copy or symlink this directory to your Hermes skills folder:

```bash
ln -s /path/to/hermes-video-editing ~/.hermes/skills/video-editing
```

## Usage

The toolkit is a CLI script (`scripts/video_toolkit.py`) that Hermes calls based on your natural language instructions.

### Examples

```
You: "Trim the first 30 seconds off this video"
→ python scripts/video_toolkit.py edit trim input.mp4 --start 00:00:30 -o output.mp4

You: "Remove the silences and add subtitles"
→ python scripts/video_toolkit.py silence remove input.mp4 -o /tmp/step1.mp4
→ python scripts/video_toolkit.py caption burn /tmp/step1.mp4 -o output.mp4

You: "Make this vertical for TikTok"
→ python scripts/video_toolkit.py enhance reframe input.mp4 --target 9:16 -o output.mp4

You: "Stabilise the shaky footage and export for YouTube"
→ python scripts/video_toolkit.py enhance stabilise input.mp4 -o /tmp/step1.mp4
→ python scripts/video_toolkit.py edit export /tmp/step1.mp4 --preset youtube -o output.mp4

You: "What's in this video?"
→ python scripts/video_toolkit.py info analyze input.mp4
→ python scripts/video_toolkit.py frames grid input.mp4 -o grid.jpg
```

### All Commands

```
info analyze INPUT                          Analyze video properties
edit trim INPUT --start T --end T           Trim between timestamps
edit concat FILE1 FILE2 [...]               Concatenate clips
edit speed INPUT --factor N                 Change speed (1.5 = 50% faster)
edit audio INPUT --audio FILE --mix N       Mix or replace audio
edit text INPUT --text "Title" --at T       Burn text overlay
edit export INPUT --preset NAME             Export with platform preset
caption generate INPUT                      Generate SRT subtitles
caption burn INPUT                          Transcribe and burn subtitles
silence remove INPUT                        Remove silent sections
scenes detect INPUT                         Detect scene changes
frames extract INPUT --interval N           Extract frames for review
frames grid INPUT                           Generate thumbnail grid
enhance stabilise INPUT                     Stabilise shaky footage
enhance bg-remove INPUT                     Remove background
enhance colour INPUT                        Auto colour enhance
enhance reframe INPUT --target 9:16         Smart reframe with face tracking
cloud runway image-to-video ...             Runway ML API (paid)
cloud shotstack ...                         Shotstack API (paid)
```

### Platform Presets

| Preset | Resolution | Notes |
|--------|-----------|-------|
| instagram-reel | 1080x1920 | 9:16, max 90s |
| instagram-post | 1080x1080 | 1:1 square, max 60s |
| youtube | 1920x1080 | 16:9, high bitrate |
| youtube-shorts | 1080x1920 | 9:16, max 60s |
| tiktok | 1080x1920 | 9:16, max 10min |
| twitter | 1280x720 | 16:9, max 2:20 |
| facebook | 1280x720 | 16:9 or 1:1 |
| telegram | 1280x720 | Streaming-optimised |

## Architecture

```
hermes-video-editing/
├── SKILL.md                    Skill definition (loaded by Hermes)
├── install.sh                  Dependency installer
├── scripts/
│   └── video_toolkit.py        Main CLI toolkit (all operations)
├── templates/
│   └── platforms.yaml          Export preset definitions
└── references/
    └── ffmpeg_reference.md     FFmpeg quick reference
```

## Requirements

- Python 3.10+
- ffmpeg (system package)
- See `install.sh` for Python package list

## License

MIT License — see [LICENSE](LICENSE).
