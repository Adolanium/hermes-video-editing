---
name: video-editing
description: Professional video editing via natural language — cut, caption, silence removal, scene detection, stabilisation, colour grading, background removal, smart reframing, and cloud API integrations. Free local tools with optional paid cloud tiers.
version: 1.0.0
category: creative
---

# Video Editing Skill

Programmatic video editing toolkit for Hermes Agent. Edit videos by describing what you want in natural language.

## Quick Reference

| Operation | Command |
|-----------|---------|
| Analyze video | `python scripts/video_toolkit.py info analyze INPUT` |
| Trim/cut | `python scripts/video_toolkit.py edit trim INPUT --start 00:01:30 --end 00:03:00 -o OUTPUT` |
| Concatenate | `python scripts/video_toolkit.py edit concat FILE1 FILE2 [FILE3 ...] -o OUTPUT` |
| Change speed | `python scripts/video_toolkit.py edit speed INPUT --factor 1.5 -o OUTPUT` |
| Add audio | `python scripts/video_toolkit.py edit audio INPUT --audio MUSIC.mp3 --mix 0.3 -o OUTPUT` |
| Burn captions | `python scripts/video_toolkit.py caption burn INPUT -o OUTPUT` |
| Generate SRT | `python scripts/video_toolkit.py caption generate INPUT -o subtitles.srt` |
| Remove silence | `python scripts/video_toolkit.py silence remove INPUT -o OUTPUT` |
| Detect scenes | `python scripts/video_toolkit.py scenes detect INPUT` |
| Extract frames | `python scripts/video_toolkit.py frames extract INPUT --interval 2 -d frames/` |
| Thumbnail grid | `python scripts/video_toolkit.py frames grid INPUT -o grid.jpg` |
| Stabilise | `python scripts/video_toolkit.py enhance stabilise INPUT -o OUTPUT` |
| Remove background | `python scripts/video_toolkit.py enhance bg-remove INPUT -o OUTPUT` |
| Auto colour | `python scripts/video_toolkit.py enhance colour INPUT -o OUTPUT` |
| Smart reframe | `python scripts/video_toolkit.py enhance reframe INPUT --target 9:16 -o OUTPUT` |
| Export preset | `python scripts/video_toolkit.py edit export INPUT --preset instagram-reel -o OUTPUT` |

## Dependencies

### Required (Tier 1 — Free, Local)
- ffmpeg (system package)
- Python 3.10+
- moviepy, ffmpeg-python, opencv-python-headless, Pillow

### Optional AI (Tier 2 — Free, Local)
- openai-whisper (transcription)
- silero (voice activity detection via torch)
- scenedetect (PySceneDetect)
- backgroundremover (background removal)
- rembg (alternative background removal)
- numpy

### Optional Cloud (Tier 2 — Paid APIs)
- Runway API (generative video, style transfer)
- Shotstack API (cloud rendering, templates)

### Install

```bash
# System dependency
sudo apt-get install ffmpeg   # Debian/Ubuntu
# brew install ffmpeg          # macOS

# Python dependencies
pip install moviepy ffmpeg-python opencv-python-headless Pillow numpy

# Optional AI tools (install individually as needed)
pip install openai-whisper    # For transcription/captions
pip install scenedetect[opencv]  # For scene detection
pip install torch             # For Silero VAD (silence detection)
pip install backgroundremover # For background removal
pip install rembg             # Alternative background removal
```

Or use the install script:
```bash
bash install.sh               # Core + all optional
bash install.sh --core        # Core only
bash install.sh --check       # Check what's installed
```

## Workflow

### 1. Receive and understand the request

Parse the user's natural language editing instructions. Common patterns:

- "Cut the first 30 seconds" → trim from 00:00:30 to end
- "Remove the bit between 2:00 and 3:30" → cut that range, concatenate the rest
- "Add subtitles" → transcribe with Whisper, burn in SRT
- "Remove silences" → Silero VAD detection, cut silent segments
- "Make it vertical for TikTok" → smart reframe to 9:16
- "Fix the shaky footage" → stabilise with vidstab
- "Make it pop more" → colour enhancement
- "Export for Instagram Reels" → reframe + export preset (1080x1920, H.264, AAC)
- "Remove the background" → backgroundremover
- "Add a lower-third title at 1:30 saying 'Chapter 2'" → text overlay at timestamp

### 2. Analyze the source video

Always start by running `info analyze` to get:
- Duration, resolution, framerate, codec, bitrate
- Audio tracks and channels
- File size

```bash
python scripts/video_toolkit.py info analyze INPUT.mp4
```

### 3. Plan the edit pipeline

Break complex requests into sequential operations. Execute in the right order:

1. **Structural edits first** (trim, cut, concatenate, silence removal)
2. **Enhancement** (stabilise, colour, background removal)
3. **Reframing/cropping** (aspect ratio changes)
4. **Overlays** (text, captions, watermarks)
5. **Audio** (music bed, normalisation, voice isolation)
6. **Export** (codec, format, platform preset)

### 4. Execute each step

Run each operation, checking the exit code and stderr. Use temporary files between steps for complex pipelines.

For multi-step edits, chain operations using temp files:
```bash
# Step 1: Remove silence
python scripts/video_toolkit.py silence remove input.mp4 -o /tmp/step1.mp4
# Step 2: Stabilise
python scripts/video_toolkit.py enhance stabilise /tmp/step1.mp4 -o /tmp/step2.mp4
# Step 3: Burn captions
python scripts/video_toolkit.py caption burn /tmp/step2.mp4 -o /tmp/step3.mp4
# Step 4: Reframe for Reels
python scripts/video_toolkit.py edit export /tmp/step3.mp4 --preset instagram-reel -o final.mp4
# Cleanup
rm /tmp/step*.mp4
```

### 5. Visual review (quality control)

After editing, **always review the result** before delivering:

```bash
# Extract frames at regular intervals for review
python scripts/video_toolkit.py frames extract OUTPUT.mp4 --interval 5 -d /tmp/review_frames/

# Generate a contact sheet / thumbnail grid
python scripts/video_toolkit.py frames grid OUTPUT.mp4 -o /tmp/review_grid.jpg
```

Then use vision_analyze to inspect:
- Are cuts clean? No black frames at edit points?
- Are captions readable and properly positioned?
- Is the framing correct for the target platform?
- Any visual artifacts or glitches?
- Is the colour/brightness consistent across edits?

If issues are found, fix and re-review.

### 6. Deliver the final file

Report to the user:
- What operations were performed
- Output file path and size
- Duration and format details
- Any warnings or notes

If the user sent the video via Telegram/Discord, send the file back as an attachment.

## Platform Export Presets

| Preset | Resolution | Framerate | Codec | Notes |
|--------|-----------|-----------|-------|-------|
| instagram-reel | 1080x1920 | 30 | H.264 | 9:16, max 90s, AAC audio |
| instagram-post | 1080x1080 | 30 | H.264 | 1:1 square, max 60s |
| youtube | 1920x1080 | 30 | H.264 | 16:9, high bitrate |
| youtube-shorts | 1080x1920 | 30 | H.264 | 9:16, max 60s |
| tiktok | 1080x1920 | 30 | H.264 | 9:16, max 10min |
| twitter | 1280x720 | 30 | H.264 | 16:9, max 2:20 |
| facebook | 1280x720 | 30 | H.264 | 16:9 or 1:1 |
| telegram | 1280x720 | 30 | H.264 | Optimised for streaming |

## Cloud API Integration (Optional, Paid)

These require API keys configured in environment variables.

### Runway ML
- `RUNWAY_API_KEY` — Generative video (text-to-video, image-to-video, video-to-video)
- Use for: AI style transfer, B-roll generation, background generation
- `python scripts/video_toolkit.py cloud runway --help`

### Shotstack
- `SHOTSTACK_API_KEY` — Cloud rendering API
- Use for: Template-driven production, data-driven personalisation, complex multi-track compositions
- `python scripts/video_toolkit.py cloud shotstack --help`

## Tips and Pitfalls

- Always analyze before editing — check duration and resolution first
- ffmpeg operations on large files can be slow on CPU — warn the user if the video is long
- Whisper transcription is the slowest operation — use the "base" model for speed, "medium" for accuracy
- Background removal on video is very slow on CPU — process frame by frame, warn about time
- When concatenating, all clips must have the same resolution and framerate — transcode first if needed
- Temp files can be large — clean up after each edit pipeline
- For Telegram delivery, files must be under 50MB — consider splitting or reducing quality
- The `--dry-run` flag on most commands shows what would happen without executing
- Use `-v` / `--verbose` for detailed ffmpeg output during debugging
