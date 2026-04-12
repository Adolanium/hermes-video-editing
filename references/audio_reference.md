# Audio Editing Quick Reference

Companion to ffmpeg_reference.md. Covers audio-specific filters, workflows, standards, and troubleshooting for AI agents doing audio work.

---

## Table of Contents

1. Note Frequency Table (C2-B5)
2. Loudness Standards & LUFS Targets
3. FFmpeg Audio Filters
4. Common Audio Workflows
5. Audio Format Comparison
6. Format Conversion Guide
7. Troubleshooting Common Audio Issues

---

## 1. Note Frequency Table (C2-B5)

Frequencies in Hz. Equal temperament, A4 = 440 Hz.

### Octave 2
| Note | Freq (Hz) | Note | Freq (Hz) |
|------|-----------|------|-----------|
| C2   | 65.41     | C#2/Db2 | 69.30 |
| D2   | 73.42     | D#2/Eb2 | 77.78 |
| E2   | 82.41     | F2   | 87.31 |
| F#2/Gb2 | 92.50  | G2   | 98.00 |
| G#2/Ab2 | 103.83 | A2   | 110.00 |
| A#2/Bb2 | 116.54 | B2   | 123.47 |

### Octave 3
| Note | Freq (Hz) | Note | Freq (Hz) |
|------|-----------|------|-----------|
| C3   | 130.81    | C#3/Db3 | 138.59 |
| D3   | 146.83    | D#3/Eb3 | 155.56 |
| E3   | 164.81    | F3   | 174.61 |
| F#3/Gb3 | 185.00  | G3   | 196.00 |
| G#3/Ab3 | 207.65  | A3   | 220.00 |
| A#3/Bb3 | 233.08  | B3   | 246.94 |

### Octave 4 (Middle C octave)
| Note | Freq (Hz) | Note | Freq (Hz) |
|------|-----------|------|-----------|
| C4   | 261.63    | C#4/Db4 | 277.18 |
| D4   | 293.66    | D#4/Eb4 | 311.13 |
| E4   | 329.63    | F4   | 349.23 |
| F#4/Gb4 | 369.99  | G4   | 392.00 |
| G#4/Ab4 | 415.30  | A4   | 440.00 |
| A#4/Bb4 | 466.16  | B4   | 493.88 |

### Octave 5
| Note | Freq (Hz) | Note | Freq (Hz) |
|------|-----------|------|-----------|
| C5   | 523.25    | C#5/Db5 | 554.37 |
| D5   | 587.33    | D#5/Eb5 | 622.25 |
| E5   | 659.26    | F5   | 698.46 |
| F#5/Gb5 | 739.99  | G5   | 783.99 |
| G#5/Ab5 | 830.61  | A5   | 880.00 |
| A#5/Bb5 | 932.33  | B5   | 987.77 |

### Quick Reference: Key Frequencies
| Musical Note | Use / Context |
|-------------|---------------|
| A4 = 440 Hz | Standard tuning reference |
| C4 = 261.63 Hz | Middle C |
| 20 Hz | Lower limit of human hearing |
| 60-80 Hz | Sub-bass (kick drums, bass synths) |
| 200-500 Hz | Warmth / muddiness zone |
| 1-4 kHz | Vocal presence |
| 2-5 kHz | Speech intelligibility |
| 6-8 kHz | Sibilance (s/sh/ch sounds) |
| 16-20 kHz | Air / sparkle (upper limit of hearing) |

### Frequency Bands for EQ Work
| Band | Range | Character |
|------|-------|-----------|
| Sub-bass | 20-60 Hz | Felt more than heard, rumble |
| Bass | 60-250 Hz | Fullness, body, warmth |
| Low-mid | 250-500 Hz | Can sound muddy if excessive |
| Mid | 500 Hz-2 kHz | Core tone, instruments |
| Upper-mid | 2-4 kHz | Bite, clarity, presence |
| Presence | 4-7 kHz | Definition, intelligibility |
| Brilliance | 7-20 kHz | Sparkle, air, hiss |

---

## 2. Loudness Standards & LUFS Targets

LUFS (Loudness Units Full Scale) = integrated loudness measurement. Lower values = quieter.

### Platform Targets
| Platform | Target (LUFS) | True Peak (dBTP) | Notes |
|----------|---------------|-------------------|-------|
| YouTube | -14 | -1.0 | Normalises to -14 LUFS |
| Spotify | -14 | -1.0 | Normalises; set normalisation OFF for intended level |
| Apple Music | -16 | -1.0 | Sound Check normalises |
| Amazon Music | -14 | -2.0 | Strict true peak |
| Tidal | -14 | -1.0 | |
| Netflix | -27 | -2.0 | Dialogue; LRA <= 10 LU |
| Broadcast (EBU R128) | -23 | -1.0 | European broadcast standard |
| Broadcast (ATSC A/85) | -24 | -2.0 | North American broadcast |
| Podcasts (Spotify/Apple) | -16 | -1.0 | General guideline |
| Podcasts (general) | -16 to -19 | -1.0 | Varies by platform |
| TikTok / Instagram | -14 to -16 | -1.0 | Auto-normalised on upload |
| CD Master | -9 to -14 | -0.3 to -1.0 | Not normalised; louder = more impact |

### Key Loudness Terms
- **Integrated LUFS**: Average loudness over the entire program
- **Short-term LUFS**: Loudness measured over 3-second windows
- **Momentary LUFS**: Loudness measured over 400ms windows
- **LRA (Loudness Range)**: Dynamic range measurement in LU; how much variation exists
- **True Peak (dBTP)**: Actual peak level including inter-sample peaks

### Rules of Thumb
- If a track sounds too quiet on a platform, it is probably being *turned down* to meet its LUFS target
- If a track sounds distorted, true peak may be exceeded
- LRA > 15 LU means the content has very high dynamic range (quiet parts much quieter than loud parts)
- For voice-only content, LRA of 5-8 LU is typical

---

## 3. FFmpeg Audio Filters

### Volume & Gain
```bash
# Simple volume adjustment (1.0 = original, 0.5 = half, 2.0 = double)
ffmpeg -i input.wav -af "volume=1.5" output.wav

# Volume in dB
ffmpeg -i input.wav -af "volume=3dB" output.wav

# Fade in (2 seconds) and fade out (3 seconds starting at 10s)
ffmpeg -i input.wav -af "afade=t=in:st=0:d=2,afade=t=out:st=10:d=3" output.wav
```

### Loudness Normalisation (two-pass for accuracy)
```bash
# Single-pass (good enough for most cases)
ffmpeg -i input.wav -af "loudnorm=I=-14:TP=-1:LRA=11" output.wav

# Two-pass (precision, measures first then applies)
# Pass 1: Measure
ffmpeg -i input.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | grep -A12 "Parsed_loudnorm"

# Pass 2: Use measured values from Pass 1 output
ffmpeg -i input.wav -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=<value>:measured_TP=<value>:measured_LRA=<value>:measured_thresh=<value>:linear=true" output.wav
```

### Equalisation (EQ)
```bash
# High-pass filter (remove rumble below 80 Hz)
ffmpeg -i input.wav -af "highpass=f=80" output.wav

# Low-pass filter (remove hiss above 15 kHz)
ffmpeg -i input.wav -af "lowpass=f=15000" output.wav

# Combine high-pass and low-pass (bandpass)
ffmpeg -i input.wav -af "highpass=f=80,lowpass=f=15000" output.wav

# Parametric EQ (boost 3 dB at 2.5 kHz, Q=1.5)
ffmpeg -i input.wav -af "equalizer=f=2500:t=q:w=1.5:g=3" output.wav

# Presence boost for dialogue (2-5 kHz)
ffmpeg -i input.wav -af "equalizer=f=3000:t=q:w=2:g=4" output.wav

# De-mud (cut 250-500 Hz region)
ffmpeg -i input.wav -af "equalizer=f=350:t=q:w=1.5:g=-3" output.wav
```

### Noise Reduction / Denoise
```bash
# Simple noise reduction with afftdn (FFT denoise)
ffmpeg -i input.wav -af "afftdn=nf=-25" output.wav

# Noise reduction with profile (two-pass)
# Pass 1: Capture noise profile from a quiet section (first 2 seconds here)
ffmpeg -i input.wav -af "afftdn=nf=-25:tn=1" -t 2 noise_profile.wav
# Then use anlr or highpass/lowpass combo

# High-pass to remove low-frequency noise (HVAC, wind, traffic rumble)
ffmpeg -i input.wav -af "highpass=f=100" output.wav

# De-hiss (reduce high-frequency noise)
ffmpeg -i input.wav -af "lowpass=f=12000,afftdn=nf=-30" output.wav
```

### Compression & Limiting
```bash
# Dynamic range compression (voice)
ffmpeg -i input.wav -af "acompressor=threshold=-20dB:ratio=4:attack=5:release=50:makeup=2" output.wav

# Hard limiter (prevent clipping)
ffmpeg -i input.wav -af "alimiter=limit=-1dB:attack=5:release=50" output.wav

# Soft clipping
ffmpeg -i input.wav -af "asoftclip" output.wav

# Multiband compression (3 bands)
ffmpeg -i input.wav -af "mcompand='.2 .2'|.05 .1|.1 .2:.01 .1  -60/-40 -40/-30 -25/-15 0/-5  20/-3:.01:.1:.1:.01:.1:.1:.01:.1'" output.wav
```

### Speed / Pitch
```bash
# Change speed WITHOUT changing pitch (atempo range: 0.5 to 100.0)
ffmpeg -i input.wav -af "atempo=1.25" output.wav

# Change speed WITH pitch shift (use rubberband if available, or rate change)
ffmpeg -i input.wav -af "asetrate=44100*1.5,aresample=44100" output.wav

# For atempo outside 0.5-2.0 range, chain filters
# Example: 3x speed (2.0 * 1.5 = 3.0)
ffmpeg -i input.wav -af "atempo=2.0,atempo=1.5" output.wav
```

### Delay, Reverb, Spatial
```bash
# Simple delay/echo
ffmpeg -i input.wav -af "adelay=500|500" output.wav

# Delay with feedback (echo effect) via aecho
ffmpeg -i input.wav -af "aecho=0.8:0.88:60:0.4" output.wav

# Stereo widening
ffmpeg -i input.wav -af "stereotools=mlev=0.5" output.wav

# Convert mono to stereo (duplicate channel)
ffmpeg -i input.wav -af "aformat=channel_layouts=stereo" output.wav

# Downmix stereo to mono
ffmpeg -i input.wav -af "pan=mono|c0=0.5*c0+0.5*c1" output.wav
# Or simply:
ffmpeg -i input.wav -ac 1 output.wav
```

### Audio Mixing & Multiple Inputs
```bash
# Mix two audio sources (equal weight)
ffmpeg -i voice.wav -i music.wav -filter_complex "[0:a][1:a]amix=inputs=2:duration=longest[a]" -map "[a]" output.wav

# Mix with different volumes (voice 100%, music 25%)
ffmpeg -i voice.wav -i music.wav -filter_complex \
  "[0:a]volume=1.0[a0];[1:a]volume=0.25[a1];[a0][a1]amix=inputs=2:duration=longest[a]" \
  -map "[a]" output.wav

# Overlay audio on video (replace existing audio)
ffmpeg -i video.mp4 -i audio.wav -c:v copy -c:a aac -map 0:v -map 1:a -shortest output.mp4

# Add audio to video (keep existing + add new)
ffmpeg -i video.mp4 -i bg_music.mp3 -filter_complex \
  "[0:a]volume=1.0[a0];[1:a]volume=0.2[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=3[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac output.mp4

# Duck background music when voice is present (sidechain compression approximation)
ffmpeg -i voice.wav -i music.wav -filter_complex \
  "[1:a]volume=0.3,adelay=0|0[music];[0:a]volume=1.0[voice];[voice][music]amix=inputs=2:duration=longest[a]" \
  -map "[a]" output.wav
```

### Audio Analysis / Measurement
```bash
# Measure LUFS / loudness (EBU R128)
ffmpeg -i input.wav -af loudnorm=print_format=json -f null - 2>&1

# Get detailed audio stream info
ffprobe -v error -show_entries stream=codec_name,sample_rate,channels,bit_rate -of json input.wav

# Waveform analysis (volumedetect)
ffmpeg -i input.wav -af volumedetect -f null - 2>&1

# Audio duration
ffprobe -v error -show_entries format=duration -of csv=p=0 input.wav

# Visualise audio spectrum (generate spectrogram image)
ffmpeg -i input.wav -lavfi showspectrumpic=s=1024x512:scale=log spectrogram.png

# Audio waveform image
ffmpeg -i input.wav -lavfi showwavespic=s=1024x256 waveform.png
```

---

## 4. Common Audio Workflows

### Workflow A: Prepare Voice-over for YouTube Video
```bash
# 1. Remove noise floor and clean up
ffmpeg -i raw_voice.wav -af "highpass=f=80,lowpass=f=14000,afftdn=nf=-25" cleaned.wav

# 2. Compress dynamics and normalise loudness
ffmpeg -i cleaned.wav -af "acompressor=threshold=-18dB:ratio=3:attack=5:release=50:makeup=2,loudnorm=I=-14:TP=-1:LRA=11" voice_final.wav
```

### Workflow B: Master a Music Track for Streaming
```bash
# 1. EQ sculpting
ffmpeg -i mixdown.wav -af "highpass=f=30,equalizer=f=250:t=q:w=1.5:g=-2,equalizer=f=8000:t=q:w=2:g=2" eq.wav

# 2. Compress and limit
ffmpeg -i eq.wav -af "acompressor=threshold=-12dB:ratio=2.5:attack=10:release=100:makeup=1,alimiter=limit=-1dB" limited.wav

# 3. Loudness normalise to -14 LUFS (two-pass for precision)
ffmpeg -i limited.wav -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1
# (use measured values in second pass as shown in section 3)
```

### Workflow C: Extract and Clean Audio from Video
```bash
# 1. Extract audio track
ffmpeg -i video.mp4 -vn -c:a pcm_s16le extracted.wav

# 2. Clean up (noise removal, EQ, compression)
ffmpeg -i extracted.wav -af "highpass=f=100,afftdn=nf=-25,acompressor=threshold=-20dB:ratio=3:attack=5:release=50,loudnorm=I=-16:TP=-1:LRA=9" clean.wav

# 3. Merge back
ffmpeg -i video.mp4 -i clean.wav -c:v copy -c:a aac -map 0:v -map 1:a output.mp4
```

### Workflow D: Create a Podcast Episode
```bash
# 1. Normalise all voice clips to -16 LUFS
for f in clip*.wav; do
  ffmpeg -i "$f" -af "highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=50,loudnorm=I=-16:TP=-1" "norm_${f}"
done

# 2. Concatenate normalised clips
echo "file 'norm_clip1.wav'" > list.txt
echo "file 'norm_clip2.wav'" >> list.txt
ffmpeg -f concat -safe 0 -i list.txt -c:a pcm_s16le combined.wav

# 3. Add intro/outro music with fade
ffmpeg -i combined.wav -i intro.wav -i outro.wav -filter_complex \
  "[1:a]afade=t=out:st=0:d=3[aintro]; \
   [0:a]asetpts=PTS-STARTPTS[voice]; \
   [2:a]afade=t=in:st=0:d=2[aoutro]; \
   [aintro][voice][aoutro]concat=n=3:v=0:a=1[a]" \
  -map "[a]" -c:a flac podcast_final.flac

# 4. Export distribution formats
ffmpeg -i podcast_final.flac -c:a libmp3lame -b:a 192k podcast.mp3
ffmpeg -i podcast_final.flac -c:a aac -b:a 128k podcast.m4a
```

### Workflow E: Batch Loudness Normalisation
```bash
# Normalise all WAV files in a directory to -14 LUFS
for f in *.wav; do
  ffmpeg -i "$f" -af "loudnorm=I=-14:TP=-1:LRA=11" -c:a pcm_s16le "norm_${f}"
done
```

---

## 5. Audio Format Comparison

| Format | Extension | Codec | Lossy/Lossless | Typical Bitrate | Sample Rates | Channels | Best For | Notes |
|--------|-----------|-------|----------------|-----------------|--------------|----------|----------|-------|
| WAV    | .wav      | pcm_s16le / pcm_s24le | Lossless | 1411 kbps (CD) | Up to 192 kHz | Up to 8 | Editing, archiving, DAW work | Uncompressed; large files; universal compatibility |
| AIFF   | .aif/.aiff | pcm_s16be | Lossless | 1411 kbps (CD) | Up to 192 kHz | Up to 6 | macOS editing, pro audio | Similar to WAV; Apple ecosystem |
| FLAC   | .flac     | flac   | Lossless (compressed) | ~800-1000 kbps | Up to 655 kHz | Up to 8 | Archiving, high-quality distribution | ~50% size of WAV; bit-perfect; metadata support |
| MP3    | .mp3      | libmp3lame | Lossy | 128-320 kbps | Up to 48 kHz | 2 | Universal distribution, legacy | Widest compatibility; patent-free since 2017 |
| AAC    | .m4a/.aac | aac    | Lossy | 96-256 kbps | Up to 96 kHz | Up to 48 | Streaming, mobile, Apple ecosystem | Better than MP3 at same bitrate; default for YouTube/Apple |
| OGG Vorbis | .ogg | libvorbis | Lossy | 64-500 kbps | Up to 192 kHz | Up to 255 | Games, Spotify (older) | Open format; good quality at low bitrates |
| Opus   | .opus     | libopus | Lossy (can do lossless) | 6-510 kbps | Up to 48 kHz | Up to 255 | VoIP, streaming, modern web | Best lossy codec; ultra-low latency; low bitrate excellence |
| ALAC   | .m4a      | alac   | Lossless | ~800 kbps | Up to 384 kHz | Up to 8 | Apple lossless archiving | Apple's FLAC equivalent |
| WMA    | .wma      | wmav2  | Lossy | 64-192 kbps | Up to 48 kHz | 2 | Legacy Windows | Avoid for new projects |

### Format Decision Tree
```
Need editing/processing?
  -> WAV (PCM 16/24-bit) or FLAC

Need universal compatibility?
  -> MP3 (320 kbps) or AAC (256 kbps)

Need smallest file size with good quality?
  -> Opus (64-128 kbps) or AAC (128 kbps)

Need lossless archiving?
  -> FLAC (half the size of WAV, identical quality)

Need lowest latency streaming/VoIP?
  -> Opus

Need Apple ecosystem compatibility?
  -> AAC (.m4a) or ALAC
```

---

## 6. Format Conversion Guide

### WAV <-> FLAC (lossless)
```bash
# WAV to FLAC
ffmpeg -i input.wav -c:a flac output.flac

# FLAC to WAV (16-bit)
ffmpeg -i input.flac -c:a pcm_s16le output.wav

# FLAC to WAV (24-bit, higher quality)
ffmpeg -i input.flac -c:a pcm_s24le output.wav
```

### To MP3
```bash
# High quality (320 kbps CBR)
ffmpeg -i input.wav -c:a libmp3lame -b:a 320k output.mp3

# Good quality (192 kbps CBR)
ffmpeg -i input.wav -c:a libmp3lame -b:a 192k output.mp3

# Variable bitrate (VBR, recommended)
ffmpeg -i input.wav -c:a libmp3lame -q:a 0 output.mp3   # ~245 kbps
ffmpeg -i input.wav -c:a libmp3lame -q:a 2 output.mp3   # ~190 kbps
```

### To AAC / M4A
```bash
# AAC 256 kbps (recommended for YouTube/Apple)
ffmpeg -i input.wav -c:a aac -b:a 256k output.m4a

# AAC 128 kbps (good for podcasts)
ffmpeg -i input.wav -c:a aac -b:a 128k -ar 44100 -ac 2 output.m4a

# AAC with native encoder (better quality at low bitrates)
ffmpeg -i input.wav -c:a aac -b:a 128k -profile:a aac_low output.m4a
```

### To Opus
```bash
# Opus 128 kbps (transparent quality for stereo music)
ffmpeg -i input.wav -c:a libopus -b:a 128k output.opus

# Opus 64 kbps (voice / podcast)
ffmpeg -i input.wav -c:a libopus -b:a 64k -ar 48000 -ac 1 output.opus

# Opus 32 kbps (low bandwidth voice)
ffmpeg -i input.wav -c:a libopus -b:a 32k -ar 16000 -ac 1 -application voip output.opus
```

### To OGG Vorbis
```bash
# OGG quality 7 (~192 kbps)
ffmpeg -i input.wav -c:a libvorbis -q:a 7 output.ogg

# OGG 128 kbps CBR
ffmpeg -i input.wav -c:a libvorbis -b:a 128k output.ogg
```

### Sample Rate Conversion
```bash
# Downsample to 44.1 kHz (CD quality)
ffmpeg -i input.wav -ar 44100 output.wav

# Upsample to 48 kHz (video standard)
ffmpeg -i input.wav -ar 48000 output.wav

# Resample with high-quality soxr resampler
ffmpeg -i input.wav -af "aresample=resampler=soxr:precision=28" -ar 48000 output.wav
```

### Channel Manipulation
```bash
# Mono to stereo
ffmpeg -i input.wav -ac 2 output.wav

# Stereo to mono (average both channels)
ffmpeg -i input.wav -ac 1 output.wav

# Extract left channel only
ffmpeg -i input.wav -af "pan=mono|c0=FL" left_only.wav

# Extract right channel only
ffmpeg -i input.wav -af "pan=mono|c0=FR" right_only.wav

# 5.1 surround to stereo downmix
ffmpeg -i input.wav -af "pan=stereo|FL=0.5*FC+0.707*FL+0.707*BL+0.5*LFE|FR=0.5*FC+0.707*FR+0.707*BR+0.5*LFE" stereo.wav
```

### Batch Format Conversion
```bash
# Convert all FLAC files to MP3 320
for f in *.flac; do
  ffmpeg -i "$f" -c:a libmp3lame -b:a 320k "${f%.flac}.mp3"
done

# Convert all WAV files to AAC, preserving folder structure
find . -name "*.wav" -exec bash -c 'ffmpeg -i "$0" -c:a aac -b:a 256k "${0%.wav}.m4a"' {} \;
```

### Bit Depth Conversion
```bash
# 24-bit to 16-bit (CD preparation) with dithering
ffmpeg -i input_24bit.wav -af "aformat=sample_fmts=s16:sample_rates=44100" -c:a pcm_s16le output_16bit.wav

# 16-bit to 32-bit float (for processing)
ffmpeg -i input.wav -c:a pcm_f32le output_f32.wav
```

---

## 7. Troubleshooting Common Audio Issues

### Audio is too quiet / too loud
```bash
# Measure current loudness
ffmpeg -i input.wav -af loudnorm=print_format=json -f null - 2>&1

# If too quiet, normalise upward
ffmpeg -i input.wav -af "loudnorm=I=-14:TP=-1" output.wav

# Quick volume boost (careful: can clip!)
ffmpeg -i input.wav -af "volume=6dB" output.wav
# Better: boost + limit
ffmpeg -i input.wav -af "volume=6dB,alimiter=limit=-1dB" output.wav
```

### Clipping / distortion
```bash
# Detect clipping
ffmpeg -i input.wav -af volumedetect -f null - 2>&1 | grep max_volume
# If max_volume is 0.0 dB, audio is clipping

# Fix: reduce level and re-normalise
ffmpeg -i input.wav -af "volume=-3dB,loudnorm=I=-14:TP=-1" output.wav

# Soft-clip to prevent harsh distortion
ffmpeg -i input.wav -af "volume=3dB,asoftclip,alimiter=limit=-1dB" output.wav
```

### Background noise (hiss, hum, rumble)
```bash
# Remove 50/60 Hz electrical hum
ffmpeg -i input.wav -af "highpass=f=100" output.wav
# For 60 Hz countries (Americas):
ffmpeg -i input.wav -af "anltrim=f=60:t=h:w=20" output.wav

# Remove hiss (broadband noise)
ffmpeg -i input.wav -af "afftdn=nf=-25" output.wav

# Remove wind/traffic rumble
ffmpeg -i input.wav -af "highpass=f=150" output.wav

# Combined clean-up chain
ffmpeg -i input.wav -af "highpass=f=100,lowpass=f=14000,afftdn=nf=-25" output.wav
```

### Audio and video out of sync
```bash
# Audio is early by 200ms (delay audio)
ffmpeg -i video.mp4 -af "adelay=200|200" -c:v copy output.mp4

# Audio is late by 200ms (speed up audio slightly or trim video start)
ffmpeg -i video.mp4 -af "atrim=start=0.2,asetpts=PTS-STARTPTS" -c:v copy output.mp4

# Using -itsoffset to shift video relative to audio
ffmpeg -itsoffset -0.2 -i video.mp4 -c:a copy -c:v libx264 output.mp4
```

### Audio drifts out of sync over time
```bash
# Force constant frame rate and resync
ffmpeg -i input.mp4 -c:v libx264 -c:a aac -vsync cfr output.mp4

# Resample audio to match video timestamps exactly
ffmpeg -i input.mp4 -c:v copy -c:a aac -ar 48000 -af "aresample=async=1" output.mp4
```

### Pops/clicks at edit points
```bash
# Add short crossfade when concatenating
ffmpeg -i clip1.wav -i clip2.wav -filter_complex \
  "[0:a]afade=t=out:st=$(DUR1-0.01):d=0.01[a0]; \
   [1:a]afade=t=in:st=0:d=0.01[a1]; \
   [a0][a1]concat=n=2:v=0:a=1[a]" \
  -map "[a]" output.wav

# Quick fix: add short fade in/out to any clip
ffmpeg -i clip.wav -af "afade=t=in:d=0.005,afade=t=out:st=$(DUR-0.005):d=0.005" output.wav
```

### Stereo channel imbalance
```bash
# Fix left-right imbalance (boost left by 3dB)
ffmpeg -i input.wav -af "pan=stereo|c0=2*c0|c1=c1,volume=0.707" output.wav

# Centre-pan a stereo file (make it mono then stereo again)
ffmpeg -i input.wav -ac 1 -ac 2 output.wav

# Swap left and right channels
ffmpeg -i input.wav -af "pan=stereo|c0=c1|c1=c0" output.wav
```

### Audio sounds "underwater" or muffled
```bash
# Boost presence and clarity
ffmpeg -i input.wav -af "equalizer=f=3000:t=q:w=2:g=4,equalizer=f=6000:t=q:w=2:g=3,highpass=f=100" output.wav

# If recorded with heavy low-pass (phone call quality), try to restore:
ffmpeg -i input.wav -af "equalizer=f=2000:t=q:w=1.5:g=4,equalizer=f=4000:t=q:w=1.5:g=3,equalizer=f=250:t=q:w=1:g=-2" output.wav
```

### "AC-3" or codec not found errors
```bash
# If ffmpeg cannot decode AC-3/EAC-3, install full build:
# Ubuntu/Debian:
sudo apt install ffmpeg
# Or use static build from https://johnvansickle.com/ffmpeg/

# Check supported codecs
ffmpeg -codecs | grep -i ac3

# Transcode AC-3 to AAC
ffmpeg -i input.mkv -c:v copy -c:a aac -b:a 256k output.mp4
```

### Sample rate mismatch issues
```bash
# Force specific sample rate
ffmpeg -i input.wav -ar 44100 output.wav

# Match sample rates when mixing
ffmpeg -i 48k.wav -i 44k.wav -filter_complex \
  "[0:a]aresample=48000[a0];[1:a]aresample=48000[a1];[a0][a1]amix=inputs=2[a]" \
  -map "[a]" -ar 48000 output.wav
```

### Extracting audio from specific container formats
```bash
# From MP4/MOV
ffmpeg -i input.mp4 -vn -c:a copy audio.aac

# From MKV
ffmpeg -i input.mkv -vn -c:a copy audio.flac   # if source was FLAC
ffmpeg -i input.mkv -vn -c:a pcm_s16le audio.wav  # convert to WAV

# From WebM
ffmpeg -i input.webm -vn -c:a libopus -b:a 128k audio.opus

# Extract specific audio track (if multiple)
ffmpeg -i input.mkv -map 0:a:1 -c:a copy second_audio_track.flac
# 0:a:0 = first audio track, 0:a:1 = second, etc.

# List all streams in a file
ffprobe -v error -show_entries stream=index,codec_type,codec_name -of csv input.mkv
```

### Quick Diagnostic Checklist
When audio problems occur, check in this order:

1. **Codec support**: `ffmpeg -codecs | grep <codec>` -- is the codec available?
2. **Stream info**: `ffprobe -show_streams input.wav` -- correct sample rate, channels, bit depth?
3. **Loudness**: `ffmpeg -i input.wav -af loudnorm=print_format=json -f null -` -- is it in expected LUFS range?
4. **Clipping**: `ffmpeg -i input.wav -af volumedetect -f null -` -- max_volume at 0.0?
5. **Sync**: Compare audio/video duration -- `ffprobe -show_entries format=duration`
6. **Phase/correlation**: If stereo sounds thin, channels may be out of phase

---

## Quick Command Cheat Sheet

```
# Extract audio from video
ffmpeg -i video.mp4 -vn -c:a pcm_s16le audio.wav

# Normalise to -14 LUFS (YouTube)
ffmpeg -i input.wav -af "loudnorm=I=-14:TP=-1:LRA=11" output.wav

# Remove background noise
ffmpeg -i input.wav -af "highpass=f=100,lowpass=f=14000,afftdn=nf=-25" output.wav

# Compress voice dynamics
ffmpeg -i voice.wav -af "acompressor=threshold=-18dB:ratio=3:attack=5:release=50" output.wav

# Mix voice + background music
ffmpeg -i voice.wav -i music.wav -filter_complex "[0:a]volume=1.0[a0];[1:a]volume=0.2[a1];[a0][a1]amix=inputs=2:duration=longest[a]" -map "[a]" output.wav

# Fade in / fade out
ffmpeg -i input.wav -af "afade=t=in:d=2,afade=t=out:st=58:d=2" output.wav

# Convert to MP3 320kbps
ffmpeg -i input.wav -c:a libmp3lame -b:a 320k output.mp3

# Batch normalise all WAVs
for f in *.wav; do ffmpeg -i "$f" -af "loudnorm=I=-14:TP=-1" "norm_$f"; done
```
