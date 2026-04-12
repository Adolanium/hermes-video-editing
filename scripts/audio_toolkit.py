#!/usr/bin/env python3
"""
audio_toolkit.py — Command-line audio editing toolkit for Hermes Agent.

Usage:
    python audio_toolkit.py info analyze INPUT
    python audio_toolkit.py edit trim INPUT --start 00:00:30 --end 00:01:00 -o OUTPUT
    python audio_toolkit.py edit fade INPUT --in 2 --out 3 -o OUTPUT
    python audio_toolkit.py edit normalise INPUT -o OUTPUT
    python audio_toolkit.py edit speed INPUT --factor 1.5 -o OUTPUT
    python audio_toolkit.py edit pitch INPUT --semitones 2 -o OUTPUT
    python audio_toolkit.py edit volume INPUT --level 1.5 -o OUTPUT
    python audio_toolkit.py edit mix INPUT --overlay VOICE --overlay-level 0.8 -o OUTPUT
    python audio_toolkit.py edit concat FILE1 FILE2 [FILE3 ...] -o OUTPUT
    python audio_toolkit.py edit convert INPUT --format mp3 --bitrate 192 -o OUTPUT
    python audio_toolkit.py generate tone --frequency 440 --duration 5 -o OUTPUT
    python audio_toolkit.py generate noise --type white --duration 3 -o OUTPUT
    python audio_toolkit.py generate pad --notes C3,Eb3,G3 --duration 10 -o OUTPUT
    python audio_toolkit.py extract VIDEO -o AUDIO
    python audio_toolkit.py replace VIDEO --audio NEW_AUDIO -o OUTPUT
    python audio_toolkit.py sync VIDEO --audio MUSIC --offset 0.5 --mix 0.3 -o OUTPUT
    python audio_toolkit.py waveform INPUT [-o waveform.png]
    python audio_toolkit.py spectrogram INPUT [-o spectrogram.png]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(cmd, **kwargs):
    """Run a subprocess command, returning CompletedProcess."""
    if isinstance(cmd, str):
        cmd = cmd.split()
    return subprocess.run(cmd, capture_output=True, text=True, timeout=600, **kwargs)


def ffprobe_json(path):
    """Get full ffprobe info as a dict."""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", str(path)
    ]
    r = run(cmd)
    if r.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {r.stderr}")
    return json.loads(r.stdout)


def get_duration(path):
    """Get duration in seconds."""
    info = ffprobe_json(path)
    fmt = info.get("format", {})
    dur = fmt.get("duration")
    if dur:
        return float(dur)
    for s in info.get("streams", []):
        if "duration" in s:
            return float(s["duration"])
    return 0.0


def format_duration(seconds):
    """Format seconds as HH:MM:SS.mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}"


def parse_timestamp(ts):
    """Parse a timestamp string (HH:MM:SS, MM:SS, or seconds) to seconds."""
    if ts is None:
        return None
    ts = str(ts).strip()
    parts = ts.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    else:
        return float(ts)


def ensure_output(path, default_suffix=".mp3"):
    """Return output path, generating one in /tmp if not provided."""
    if path:
        return Path(path)
    return Path(tempfile.mktemp(suffix=default_suffix))


# ---------------------------------------------------------------------------
# Note frequency helper (for generate pad)
# ---------------------------------------------------------------------------

NOTE_MAP = {
    "C2": 65.41, "C#2": 69.30, "Db2": 69.30, "D2": 73.42, "D#2": 77.78,
    "Eb2": 77.78, "E2": 82.41, "F2": 87.31, "F#2": 92.50, "Gb2": 92.50,
    "G2": 98.00, "G#2": 103.83, "Ab2": 103.83, "A2": 110.00, "A#2": 116.54,
    "Bb2": 116.54, "B2": 123.47,
    "C3": 130.81, "C#3": 138.59, "Db3": 138.59, "D3": 146.83, "D#3": 155.56,
    "Eb3": 155.56, "E3": 164.81, "F3": 174.61, "F#3": 185.00, "Gb3": 185.00,
    "G3": 196.00, "G#3": 207.65, "Ab3": 207.65, "A3": 220.00, "A#3": 233.08,
    "Bb3": 233.08, "B3": 246.94,
    "C4": 261.63, "C#4": 277.18, "Db4": 277.18, "D4": 293.66, "D#4": 311.13,
    "Eb4": 311.13, "E4": 329.63, "F4": 349.23, "F#4": 369.99, "Gb4": 369.99,
    "G4": 392.00, "G#4": 415.30, "Ab4": 415.30, "A4": 440.00, "A#4": 466.16,
    "Bb4": 466.16, "B4": 493.88,
    "C5": 523.25, "D5": 587.33, "E5": 659.26, "F5": 698.46, "G5": 783.99,
    "A5": 880.00, "B5": 987.77,
}


# ---------------------------------------------------------------------------
# Info / Analysis
# ---------------------------------------------------------------------------

def cmd_info_analyze(args):
    """Analyze an audio file and print its properties."""
    path = Path(args.input)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    info = ffprobe_json(path)
    fmt = info.get("format", {})
    streams = info.get("streams", [])

    print(f"File: {path}")
    print(f"Size: {int(fmt.get('size', 0)) / 1024 / 1024:.1f} MB")
    print(f"Duration: {format_duration(float(fmt.get('duration', 0)))}")
    print(f"Format: {fmt.get('format_long_name', 'unknown')}")
    print(f"Bitrate: {int(fmt.get('bit_rate', 0)) / 1000:.0f} kbps")
    print()

    for s in streams:
        codec_type = s.get("codec_type")
        if codec_type == "audio":
            codec = s.get("codec_name", "?")
            channels = s.get("channels", "?")
            channel_layout = s.get("channel_layout", "")
            sample_rate = s.get("sample_rate", "?")
            bit_depth = s.get("bits_per_sample", s.get("bits_per_raw_sample", "?"))
            print(f"Audio: {codec}, {channels} ch ({channel_layout}), {sample_rate} Hz, {bit_depth}-bit")

            # Calculate loudness stats if possible
            r = run([
                "ffmpeg", "-i", str(path), "-af",
                "astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=/dev/stderr",
                "-f", "null", "-"
            ])
            if r.stderr:
                for line in r.stderr.split("\n"):
                    if "RMS_level" in line and "=" in line:
                        try:
                            val = line.split("=")[-1].strip()
                            db = float(val)
                            print(f"RMS Level: {db:.1f} dB")
                        except (ValueError, IndexError):
                            pass

    return 0


# ---------------------------------------------------------------------------
# Edit operations
# ---------------------------------------------------------------------------

def cmd_edit_trim(args):
    """Trim audio between start and end timestamps."""
    inp = Path(args.input)
    out = ensure_output(args.output)
    start = parse_timestamp(args.start)
    end = parse_timestamp(args.end)

    cmd = ["ffmpeg", "-y", "-i", str(inp)]
    if start is not None:
        cmd += ["-ss", format_duration(start)]
    if end is not None:
        cmd += ["-to", format_duration(end)]
    cmd += ["-c:a", "libmp3lame", "-q:a", "2", str(out)]

    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Trimmed: {out} ({format_duration(get_duration(str(out)))})")
    return 0


def cmd_edit_fade(args):
    """Apply fade in and/or fade out to audio."""
    inp = Path(args.input)
    out = ensure_output(args.output)
    fade_in = float(args.fade_in) if args.fade_in else 0
    fade_out = float(args.fade_out) if args.fade_out else 0

    filters = []
    if fade_in > 0:
        filters.append(f"afade=t=in:st=0:d={fade_in}")
    if fade_out > 0:
        dur = get_duration(str(inp))
        start = max(0, dur - fade_out)
        filters.append(f"afade=t=out:st={start}:d={fade_out}")

    if not filters:
        print("Error: specify at least one of --fade-in or --fade-out", file=sys.stderr)
        return 1

    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-af", ",".join(filters),
        "-c:a", "libmp3lame", "-q:a", "2",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Faded: {out}")
    return 0


def cmd_edit_normalise(args):
    """Normalise audio loudness to broadcast standard (-16 LUFS)."""
    inp = Path(args.input)
    out = ensure_output(args.output)
    target = float(args.target) if args.target else -16.0
    tp = float(args.true_peak) if args.true_peak else -1.5
    lra = float(args.lra) if args.lra else 11.0

    # Two-pass loudnorm for precision
    # Pass 1: measure
    cmd1 = [
        "ffmpeg", "-y", "-i", str(inp),
        "-af", f"loudnorm=I={target}:TP={tp}:LRA={lra}:print_format=json",
        "-f", "null", "-"
    ]
    r = run(cmd1)
    if r.returncode != 0:
        print(f"Error (pass 1): {r.stderr}", file=sys.stderr)
        return 1

    # Parse loudnorm stats
    stats = None
    for line in r.stderr.split("\n"):
        if '"target_offset"' in line:
            # Found the JSON block
            json_start = r.stderr.index("{", r.stderr.index("loudnorm"))
            json_end = r.stderr.rindex("}") + 1
            stats = json.loads(r.stderr[json_start:json_end])
            break

    if stats:
        # Pass 2: apply with measured values
        cmd2 = [
            "ffmpeg", "-y", "-i", str(inp),
            "-af", (
                f"loudnorm=I={target}:TP={tp}:LRA={lra}"
                f":measured_I={stats.get('input_i', 0)}"
                f":measured_TP={stats.get('input_tp', 0)}"
                f":measured_LRA={stats.get('input_lra', 0)}"
                f":measured_thresh={stats.get('input_thresh', 0)}"
                f":offset={stats.get('target_offset', 0)}"
                f":linear=true"
            ),
            "-c:a", "libmp3lame", "-q:a", "2",
            str(out)
        ]
        r = run(cmd2)
    else:
        # Fallback: single-pass
        cmd2 = [
            "ffmpeg", "-y", "-i", str(inp),
            "-af", f"loudnorm=I={target}:TP={tp}:LRA={lra}",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(out)
        ]
        r = run(cmd2)

    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1

    old_loud = stats.get("input_i", "?") if stats else "?"
    print(f"Normalised: {out} (was {old_loud} LUFS, target {target} LUFS)")
    return 0


def cmd_edit_speed(args):
    """Change audio playback speed (affects pitch)."""
    inp = Path(args.input)
    out = ensure_output(args.output)
    factor = float(args.factor)

    # atempo supports 0.5 to 100.0; chain if needed
    if factor < 0.5:
        af = f"atempo=0.5,atempo={factor/0.5}"
    elif factor > 100:
        af = f"atempo=100,atempo={factor/100}"
    else:
        af = f"atempo={factor}"

    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-af", af,
        "-c:a", "libmp3lame", "-q:a", "2",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Speed x{factor}: {out} ({format_duration(get_duration(str(out)))})")
    return 0


def cmd_edit_pitch(args):
    """Shift pitch without changing speed using rubberband or asetrate."""
    inp = Path(args.input)
    out = ensure_output(args.output)
    semitones = float(args.semitones)

    # Use asetrate + atempo for pitch shift
    # Pitch multiplier from semitones: 2^(semitones/12)
    pitch_mult = 2 ** (semitones / 12.0)

    # This changes both pitch and speed, then we compensate speed
    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-af", f"asetrate=44100*{pitch_mult},aresample=44100",
        "-c:a", "libmp3lame", "-q:a", "2",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    direction = "up" if semitones > 0 else "down"
    print(f"Pitch shifted {direction} {abs(semitones)} semitones: {out}")
    return 0


def cmd_edit_volume(args):
    """Adjust audio volume level."""
    inp = Path(args.input)
    out = ensure_output(args.output)
    level = float(args.level)

    # Level can be a multiplier (1.5 = 50% louder) or dB (+3dB)
    if args.db:
        af = f"volume={level}dB"
    else:
        af = f"volume={level}"

    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-af", af,
        "-c:a", "libmp3lame", "-q:a", "2",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    unit = "dB" if args.db else "x"
    print(f"Volume adjusted ({level}{unit}): {out}")
    return 0


def cmd_edit_mix(args):
    """Mix multiple audio tracks together."""
    inp = Path(args.input)
    overlays = args.overlay
    overlay_levels = [float(x) for x in (args.overlay_level or ["0.8"] * len(overlays))]
    main_level = float(args.main_level) if args.main_level else 1.0
    out = ensure_output(args.output)

    # Pad overlay_levels to match overlays
    while len(overlay_levels) < len(overlays):
        overlay_levels.append(overlay_levels[-1])

    # Build filter: main track + overlays mixed
    inputs = ["-i", str(inp)]
    for ov in overlays:
        inputs += ["-i", str(ov)]

    filter_parts = [f"[0:a]volume={main_level}[a0]"]
    for i, level in enumerate(overlay_levels):
        filter_parts.append(f"[{i+1}:a]volume={level}[a{i+1}]")

    mix_inputs = "".join(f"[a{i}]" for i in range(len(overlays) + 1))
    filter_parts.append(f"{mix_inputs}amix=inputs={len(overlays)+1}:duration=longest[a]")

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", ";".join(filter_parts),
        "-map", "[a]",
        "-c:a", "libmp3lame", "-q:a", "2",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Mixed {len(overlays)+1} tracks: {out}")
    return 0


def cmd_edit_concat(args):
    """Concatenate multiple audio files."""
    files = args.inputs
    out = ensure_output(args.output)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for fp in files:
            f.write(f"file '{Path(fp).resolve()}'\n")
        concat_file = f.name

    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:a", "libmp3lame", "-q:a", "2",
        str(out)
    ]
    r = run(cmd)
    os.unlink(concat_file)

    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Concatenated {len(files)} files: {out} ({format_duration(get_duration(str(out)))})")
    return 0


def cmd_edit_convert(args):
    """Convert audio between formats."""
    inp = Path(args.input)
    out = ensure_output(args.output, default_suffix=f".{args.format or 'mp3'}")
    fmt = args.format or "mp3"
    bitrate = args.bitrate or "192"
    sample_rate = args.sample_rate or "44100"
    channels = args.channels or "2"

    codec_map = {
        "mp3": ["-c:a", "libmp3lame", "-b:a", f"{bitrate}k"],
        "wav": ["-c:a", "pcm_s16le"],
        "aac": ["-c:a", "aac", "-b:a", f"{bitrate}k"],
        "ogg": ["-c:a", "libvorbis", "-q:a", "5"],
        "flac": ["-c:a", "flac"],
        "m4a": ["-c:a", "aac", "-b:a", f"{bitrate}k"],
        "opus": ["-c:a", "libopus", "-b:a", f"{bitrate}k"],
    }

    codec_args = codec_map.get(fmt, codec_map["mp3"])

    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-ar", sample_rate, "-ac", channels,
        *codec_args,
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    info = ffprobe_json(str(out))
    codec = "?"
    for s in info.get("streams", []):
        if s.get("codec_type") == "audio":
            codec = s.get("codec_name", "?")
    print(f"Converted to {fmt}/{codec}: {out} ({format_duration(get_duration(str(out)))})")
    return 0


# ---------------------------------------------------------------------------
# Generate
# ---------------------------------------------------------------------------

def cmd_generate_tone(args):
    """Generate a pure tone."""
    out = ensure_output(args.output, default_suffix=".mp3")
    freq = float(args.frequency) if args.frequency else 440
    duration = float(args.duration) if args.duration else 5
    sample_rate = args.sample_rate or "44100"
    waveform = args.waveform or "sine"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"{waveform}=frequency={freq}:duration={duration}:sample_rate={sample_rate}",
        "-c:a", "libmp3lame", "-q:a", "2",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Tone ({waveform}, {freq}Hz, {duration}s): {out}")
    return 0


def cmd_generate_noise(args):
    """Generate coloured noise."""
    out = ensure_output(args.output, default_suffix=".mp3")
    noise_type = args.type or "white"
    duration = float(args.duration) if args.duration else 3
    volume = float(args.volume) if args.volume else 0.5

    # Use anullsrc with noise filter
    noise_colors = {
        "white": "0",      # all frequencies equal
        "pink": "1",        # 1/f
        "brown": "2",       # 1/f^2
        "blue": "3",        # f
        "violet": "4",      # f^2
    }

    colour_param = noise_colors.get(noise_type, "0")

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i",
        f"sine=frequency=1:duration={duration},"
        f"anoisesrc=d={duration}:c={colour_param}:a={volume}",
        "-c:a", "libmp3lame", "-q:a", "2",
        "-t", str(duration),
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        # Fallback: use sox-style noise generation
        cmd2 = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i",
            f"anoisesrc=d={duration}:c={colour_param}:a={volume}",
            "-c:a", "libmp3lame", "-q:a", "2",
            str(out)
        ]
        r = run(cmd2)
        if r.returncode != 0:
            print(f"Error: {r.stderr}", file=sys.stderr)
            return 1

    print(f"{noise_type.capitalize()} noise ({duration}s): {out}")
    return 0


def cmd_generate_pad(args):
    """Generate an ambient pad from a chord (multiple sine tones)."""
    out = ensure_output(args.output, default_suffix=".mp3")
    notes_str = args.notes
    duration = float(args.duration) if args.duration else 10
    volume = float(args.volume) if args.volume else 0.15
    lowpass_freq = int(args.lowpass) if args.lowpass else 400
    fade_time = float(args.fade) if args.fade else 2.0

    # Parse notes: "C3,Eb3,G3" -> frequencies
    notes = [n.strip() for n in notes_str.split(",")]
    freqs = []
    for n in notes:
        if n in NOTE_MAP:
            freqs.append(NOTE_MAP[n])
        else:
            try:
                freqs.append(float(n))
            except ValueError:
                print(f"Warning: unknown note '{n}', skipping", file=sys.stderr)

    if not freqs:
        print("Error: no valid notes specified", file=sys.stderr)
        return 1

    # Build ffmpeg command with multiple sine inputs, mixed
    inputs = []
    for f in freqs:
        inputs += ["-f", "lavfi", "-i", f"sine=frequency={f}:duration={duration}"]

    # Mix all tones, apply low-pass filter and fade
    n_inputs = len(freqs)
    mix_inputs = "".join(f"[{i}:a]" for i in range(n_inputs))
    filter_complex = (
        f"{mix_inputs}amix=inputs={n_inputs}:duration=longest,"
        f"volume={volume},"
        f"lowpass=f={lowpass_freq},"
        f"afade=t=in:st=0:d={fade_time},"
        f"afade=t=out:st={duration - fade_time}:d={fade_time}"
        f"[a]"
    )

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_complex,
        "-map", "[a]",
        "-c:a", "libmp3lame", "-q:a", "2",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1

    note_names = ",".join(notes)
    print(f"Pad ({note_names}, {duration}s, lowpass {lowpass_freq}Hz): {out}")
    return 0


# ---------------------------------------------------------------------------
# Extract / Replace / Sync (video-audio operations)
# ---------------------------------------------------------------------------

def cmd_extract(args):
    """Extract audio track from a video file."""
    inp = Path(args.input)
    out = ensure_output(args.output, default_suffix=".mp3")
    fmt = args.format or "mp3"

    codec_map = {
        "mp3": ["-c:a", "libmp3lame", "-q:a", "2"],
        "wav": ["-c:a", "pcm_s16le"],
        "aac": ["-c:a", "aac", "-b:a", "192k"],
        "flac": ["-c:a", "flac"],
        "ogg": ["-c:a", "libvorbis", "-q:a", "5"],
        "opus": ["-c:a", "libopus", "-b:a", "128k"],
    }

    codec_args = codec_map.get(fmt, codec_map["mp3"])

    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-vn", *codec_args,
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Extracted ({fmt}): {out} ({format_duration(get_duration(str(out)))})")
    return 0


def cmd_replace(args):
    """Replace audio track in a video file."""
    inp = Path(args.input)
    audio = Path(args.audio)
    out = ensure_output(args.output, default_suffix=".mp4")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(inp), "-i", str(audio),
        "-c:v", "copy", "-c:a", "aac",
        "-map", "0:v", "-map", "1:a",
        "-shortest", "-movflags", "+faststart",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Audio replaced: {out}")
    return 0


def cmd_sync(args):
    """Sync audio to video with offset, mixing, and ducking."""
    inp = Path(args.input)
    audio = Path(args.audio)
    out = ensure_output(args.output, default_suffix=".mp4")
    offset = float(args.offset) if args.offset else 0
    mix_level = float(args.mix) if args.mix else 0.3
    duck = args.duck

    if duck:
        # Side-chain ducking: lower music when video audio is present
        filter_complex = (
            f"[0:a]volume=1.0[original];"
            f"[1:a]adelay={int(offset*1000)}|{int(offset*1000)},volume={mix_level}[music];"
            f"[original][music]sidechaincompress=threshold=0.1:ratio=4:attack=10:release=200,"
            f"amix=inputs=2:duration=longest[a]"
        )
    else:
        filter_complex = (
            f"[0:a]volume=1.0[original];"
            f"[1:a]adelay={int(offset*1000)}|{int(offset*1000)},volume={mix_level}[music];"
            f"[original][music]amix=inputs=2:duration=longest:dropout_transition=3[a]"
        )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(inp), "-i", str(audio),
        "-filter_complex", filter_complex,
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    features = []
    if offset > 0:
        features.append(f"offset {offset}s")
    if duck:
        features.append("ducking")
    features_str = f" ({', '.join(features)})" if features else ""
    print(f"Audio synced{features_str}: {out}")
    return 0


# ---------------------------------------------------------------------------
# Visualisation
# ---------------------------------------------------------------------------

def cmd_waveform(args):
    """Generate a waveform image of the audio."""
    inp = Path(args.input)
    out = ensure_output(args.output, default_suffix=".png")
    width = int(args.width) if args.width else 1200
    height = int(args.height) if args.height else 300
    colour = args.color or "steelblue"

    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-filter_complex",
        f"[0:a]showwavespic=s={width}x{height}:colors={colour}",
        "-frames:v", "1",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Waveform: {out}")
    return 0


def cmd_spectrogram(args):
    """Generate a spectrogram image of the audio."""
    inp = Path(args.input)
    out = ensure_output(args.output, default_suffix=".png")
    width = int(args.width) if args.width else 1200
    height = int(args.height) if args.height else 512

    cmd = [
        "ffmpeg", "-y", "-i", str(inp),
        "-filter_complex",
        f"[0:a]showspectrumpic=s={width}x{height}:legend=1",
        "-frames:v", "1",
        str(out)
    ]
    r = run(cmd)
    if r.returncode != 0:
        print(f"Error: {r.stderr}", file=sys.stderr)
        return 1
    print(f"Spectrogram: {out}")
    return 0


# ---------------------------------------------------------------------------
# Main argument parser
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Audio Editing Toolkit for Hermes Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="group")

    # info
    p_info = sub.add_parser("info")
    p_info_sub = p_info.add_subparsers(dest="command")
    p_analyze = p_info_sub.add_parser("analyze", help="Analyze audio properties")
    p_analyze.add_argument("input")

    # edit
    p_edit = sub.add_parser("edit")
    p_edit_sub = p_edit.add_subparsers(dest="command")

    p_trim = p_edit_sub.add_parser("trim", help="Trim audio")
    p_trim.add_argument("input")
    p_trim.add_argument("--start", help="Start timestamp")
    p_trim.add_argument("--end", help="End timestamp")
    p_trim.add_argument("-o", "--output")

    p_fade = p_edit_sub.add_parser("fade", help="Apply fade in/out")
    p_fade.add_argument("input")
    p_fade.add_argument("--fade-in", dest="fade_in", help="Fade in duration (seconds)")
    p_fade.add_argument("--fade-out", dest="fade_out", help="Fade out duration (seconds)")
    p_fade.add_argument("-o", "--output")

    p_norm = p_edit_sub.add_parser("normalise", help="Normalise loudness (EBU R128)")
    p_norm.add_argument("input")
    p_norm.add_argument("--target", help="Target LUFS (default: -16)")
    p_norm.add_argument("--true-peak", dest="true_peak", help="True peak dB (default: -1.5)")
    p_norm.add_argument("--lra", help="Loudness range (default: 11)")
    p_norm.add_argument("-o", "--output")

    p_speed = p_edit_sub.add_parser("speed", help="Change speed")
    p_speed.add_argument("input")
    p_speed.add_argument("--factor", required=True, help="Speed factor (1.5 = 50%% faster)")
    p_speed.add_argument("-o", "--output")

    p_pitch = p_edit_sub.add_parser("pitch", help="Shift pitch in semitones")
    p_pitch.add_argument("input")
    p_pitch.add_argument("--semitones", required=True, help="Semitones to shift (positive=up)")
    p_pitch.add_argument("-o", "--output")

    p_vol = p_edit_sub.add_parser("volume", help="Adjust volume")
    p_vol.add_argument("input")
    p_vol.add_argument("--level", required=True, help="Volume level (1.5=50%% louder, or dB value)")
    p_vol.add_argument("--db", action="store_true", help="Treat level as decibels")
    p_vol.add_argument("-o", "--output")

    p_mix = p_edit_sub.add_parser("mix", help="Mix multiple audio tracks")
    p_mix.add_argument("input", help="Main audio file")
    p_mix.add_argument("--overlay", required=True, action="append", help="Overlay audio file (can repeat)")
    p_mix.add_argument("--overlay-level", dest="overlay_level", action="append", help="Level per overlay")
    p_mix.add_argument("--main-level", dest="main_level", help="Main track level (default: 1.0)")
    p_mix.add_argument("-o", "--output")

    p_concat = p_edit_sub.add_parser("concat", help="Concatenate audio files")
    p_concat.add_argument("inputs", nargs="+")
    p_concat.add_argument("-o", "--output")

    p_convert = p_edit_sub.add_parser("convert", help="Convert audio format")
    p_convert.add_argument("input")
    p_convert.add_argument("--format", default="mp3", choices=["mp3", "wav", "aac", "ogg", "flac", "m4a", "opus"])
    p_convert.add_argument("--bitrate", default="192", help="Bitrate in kbps")
    p_convert.add_argument("--sample-rate", dest="sample_rate", help="Sample rate (default: 44100)")
    p_convert.add_argument("--channels", help="Channels (1=mono, 2=stereo)")
    p_convert.add_argument("-o", "--output")

    # generate
    p_gen = sub.add_parser("generate")
    p_gen_sub = p_gen.add_subparsers(dest="command")

    p_tone = p_gen_sub.add_parser("tone", help="Generate a pure tone")
    p_tone.add_argument("--frequency", default="440", help="Frequency in Hz")
    p_tone.add_argument("--duration", default="5", help="Duration in seconds")
    p_tone.add_argument("--waveform", default="sine", choices=["sine", "square", "sawtooth", "triangle"])
    p_tone.add_argument("--sample-rate", dest="sample_rate", default="44100")
    p_tone.add_argument("-o", "--output")

    p_noise = p_gen_sub.add_parser("noise", help="Generate coloured noise")
    p_noise.add_argument("--type", default="white", choices=["white", "pink", "brown", "blue", "violet"])
    p_noise.add_argument("--duration", default="3")
    p_noise.add_argument("--volume", default="0.5")
    p_noise.add_argument("-o", "--output")

    p_pad = p_gen_sub.add_parser("pad", help="Generate ambient pad chord")
    p_pad.add_argument("--notes", required=True, help="Comma-separated notes (e.g. C3,Eb3,G3)")
    p_pad.add_argument("--duration", default="10")
    p_pad.add_argument("--volume", default="0.15")
    p_pad.add_argument("--lowpass", default="400", help="Low-pass filter frequency")
    p_pad.add_argument("--fade", default="2", help="Fade in/out duration")
    p_pad.add_argument("-o", "--output")

    # extract / replace / sync
    p_extract = sub.add_parser("extract")
    p_extract.add_argument("input", help="Video file to extract audio from")
    p_extract.add_argument("--format", default="mp3", choices=["mp3", "wav", "aac", "flac", "ogg", "opus"])
    p_extract.add_argument("-o", "--output")

    p_replace = sub.add_parser("replace")
    p_replace.add_argument("input", help="Video file")
    p_replace.add_argument("--audio", required=True, help="New audio file")
    p_replace.add_argument("-o", "--output")

    p_sync = sub.add_parser("sync")
    p_sync.add_argument("input", help="Video file")
    p_sync.add_argument("--audio", required=True, help="Audio to sync")
    p_sync.add_argument("--offset", default="0", help="Audio delay in seconds")
    p_sync.add_argument("--mix", default="0.3", help="Mix level for added audio")
    p_sync.add_argument("--duck", action="store_true", help="Enable ducking (lower music when speech present)")
    p_sync.add_argument("-o", "--output")

    # visualisation
    p_wave = sub.add_parser("waveform")
    p_wave.add_argument("input")
    p_wave.add_argument("--width", default="1200")
    p_wave.add_argument("--height", default="300")
    p_wave.add_argument("--color", default="steelblue")
    p_wave.add_argument("-o", "--output")

    p_spec = sub.add_parser("spectrogram")
    p_spec.add_argument("input")
    p_spec.add_argument("--width", default="1200")
    p_spec.add_argument("--height", default="512")
    p_spec.add_argument("-o", "--output")

    args = parser.parse_args()

    if not args.group:
        parser.print_help()
        return 1

    dispatch = {
        ("info", "analyze"): cmd_info_analyze,
        ("edit", "trim"): cmd_edit_trim,
        ("edit", "fade"): cmd_edit_fade,
        ("edit", "normalise"): cmd_edit_normalise,
        ("edit", "speed"): cmd_edit_speed,
        ("edit", "pitch"): cmd_edit_pitch,
        ("edit", "volume"): cmd_edit_volume,
        ("edit", "mix"): cmd_edit_mix,
        ("edit", "concat"): cmd_edit_concat,
        ("edit", "convert"): cmd_edit_convert,
        ("generate", "tone"): cmd_generate_tone,
        ("generate", "noise"): cmd_generate_noise,
        ("generate", "pad"): cmd_generate_pad,
        ("extract", None): cmd_extract,
        ("replace", None): cmd_replace,
        ("sync", None): cmd_sync,
        ("waveform", None): cmd_waveform,
        ("spectrogram", None): cmd_spectrogram,
    }

    handler = dispatch.get((args.group, getattr(args, "command", None)))
    if handler:
        return handler(args)
    else:
        parser.parse_args(["--help"])
        return 1


if __name__ == "__main__":
    sys.exit(main() or 0)
