# FFmpeg Quick Reference for Video Editing

## Common Operations

### Trim/cut
```bash
# Cut from timestamp to end
ffmpeg -i input.mp4 -ss 00:01:30 -c:v libx264 -c:a aac -movflags +faststart output.mp4

# Cut between two timestamps
ffmpeg -i input.mp4 -ss 00:01:30 -to 00:03:00 -c:v libx264 -c:a aac output.mp4

# Fast seek (put -ss before -i for instant seek, less precise)
ffmpeg -ss 00:01:30 -i input.mp4 -t 60 -c:v libx264 -c:a aac output.mp4
```

### Concatenate
```bash
# Create file list
echo "file 'clip1.mp4'" > list.txt
echo "file 'clip2.mp4'" >> list.txt
ffmpeg -f concat -safe 0 -i list.txt -c:v libx264 -c:a aac output.mp4
```

### Speed change
```bash
# 2x speed (video only)
ffmpeg -i input.mp4 -filter:v "setpts=0.5*PTS" -an output.mp4

# 2x speed (video + audio)
ffmpeg -i input.mp4 -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2[a]" -map "[v]" -map "[a]" output.mp4
```

### Text overlay
```bash
ffmpeg -i input.mp4 -vf "drawtext=text='Title':fontsize=48:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=h-text_h-40" -c:a copy output.mp4
```

### Subtitle burn-in
```bash
ffmpeg -i input.mp4 -vf "subtitles=subs.srt:force_style='FontSize=24,PrimaryColour=&Hffffff,OutlineColour=&H000000'" -c:a copy output.mp4
```

### Audio
```bash
# Replace audio track
ffmpeg -i input.mp4 -i music.mp3 -c:v copy -c:a aac -map 0:v -map 1:a -shortest output.mp4

# Mix audio (original at 100%, music at 30%)
ffmpeg -i input.mp4 -i music.mp3 -filter_complex "[0:a]volume=1.0[a0];[1:a]volume=0.3[a1];[a0][a1]amix=inputs=2:duration=longest[a]" -map 0:v -map "[a]" -c:v copy -c:a aac output.mp4

# Normalise audio
ffmpeg -i input.mp4 -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:v copy output.mp4
```

### Stabilise
```bash
# Pass 1: analyse
ffmpeg -i input.mp4 -vf "vidstabdetect=result=transforms.trf:shakiness=5" -f null -
# Pass 2: apply
ffmpeg -i input.mp4 -vf "vidstabtransform=input=transforms.trf:smoothing=10:optzoom=1" -c:v libx264 -c:a aac output.mp4
```

### Colour correction
```bash
# Auto brightness/contrast boost
ffmpeg -i input.mp4 -vf "eq=brightness=0.05:contrast=1.1:saturation=1.1" -c:a copy output.mp4

# Denoise
ffmpeg -i input.mp4 -vf "hqdn3d=4:3:6:4.5" -c:a copy output.mp4
```

### Scale / reframe
```bash
# Scale to 1080p with letterboxing
ffmpeg -i input.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" -c:a aac output.mp4
```

### Frame extraction
```bash
# 1 frame per second
ffmpeg -i input.mp4 -vf fps=1 frames/frame_%04d.jpg

# Keyframes only
ffmpeg -skip_frame nokey -i input.mp4 -vsync 0 -f image2 keyframes/%04d.jpg

# Specific timestamp
ffmpeg -ss 00:02:30 -i input.mp4 -frames:v 1 snapshot.jpg
```

### Format conversion
```bash
# To H.264/AAC (universal compatibility)
ffmpeg -i input.avi -c:v libx264 -c:a aac -movflags +faststart output.mp4

# To GIF
ffmpeg -i input.mp4 -vf "fps=12,scale=480:-1:flags=lanczos" -loop 0 output.gif
```

## Codecs Reference

| Codec | Type | Use case |
|-------|------|----------|
| libx264 | Video | Universal H.264 encoding |
| libx265 | Video | H.265/HEVC (better compression, slower) |
| libvpx-vp9 | Video | WebM with alpha channel support |
| aac | Audio | Universal audio codec |
| libmp3lame | Audio | MP3 encoding |
| copy | Both | Stream copy (no re-encode, instant) |

## Flags

- `-movflags +faststart` — Move metadata to front (web streaming)
- `-crf 23` — Constant quality (lower = better, 18-28 range)
- `-preset medium` — Encoding speed (ultrafast/superfast/veryfast/faster/fast/medium/slow/slower/veryslow)
- `-an` — No audio
- `-vn` — No video
- `-y` — Overwrite output without asking
