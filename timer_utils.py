#!/usr/bin/env python3
"""Common utilities for timer video generators."""

import os
import random
import math
from pathlib import Path
from PIL import ImageFont


# Common Configuration
RESOLUTION = (1920, 1080)
BACKGROUND_COLOR = "black"
TEXT_COLOR = "red"
FONT_SIZE = 700
USE_GPU = True


def format_time(seconds: float) -> str:
    """Format seconds as MM:SS."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def load_digital_font(font_size: int = FONT_SIZE):
    """Try to load a digital-style font, fallback to default if not found."""
    home = Path.home()
    digital_fonts = [
        str(home / ".fonts/digital-7 (mono).ttf"),
        str(home / ".fonts/digital-7.ttf"),
        "/usr/share/fonts/truetype/digital-7/digital-7.ttf",
        "Digital-7 Mono",
        "Digital-7",
        "digital-7",
        "LCD",
        "DSEG7Classic-Bold",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    ]

    for font_name in digital_fonts:
        try:
            font = ImageFont.truetype(font_name, font_size)
            print(f"Using font: {font_name}")
            return font
        except (OSError, IOError):
            continue

    print("Warning: No digital font found. Install 'Digital-7' or similar for best results.")
    print("Download from: https://www.1001fonts.com/digital-7-font.html")
    return ImageFont.load_default()


def get_codec_config(use_gpu: bool = USE_GPU):
    """Get codec and ffmpeg parameters based on GPU availability."""
    if use_gpu:
        os.environ["LIBVA_DRIVER_NAME"] = "radeonsi"
        codec = "h264_vaapi"
        ffmpeg_params = [
            "-init_hw_device",
            "vaapi=va:/dev/dri/renderD128",
            "-filter_hw_device",
            "va",
            "-vf",
            "format=nv12,hwupload",
            "-qp",
            "23",
        ]
        print(f"  Codec: {codec} (AMD GPU accelerated via VAAPI)")
    else:
        codec = "libx264"
        ffmpeg_params = ["-preset", "medium", "-crf", "23"]
        print(f"  Codec: {codec} (CPU)")

    return codec, ffmpeg_params


def corrupt_digit(char: str, corruption_chance: float = 0.997) -> str:
    """Randomly corrupt a digit to look glitchy."""
    if random.random() > corruption_chance:
        corruption_map = {
            "0": ["O", "0", "D"],
            "1": ["I", "1", "|", "l"],
            "2": ["Z", "2", "z"],
            "3": ["3", "E"],
            "4": ["4", "A"],
            "5": ["S", "5", "s"],
            "6": ["6", "G", "b"],
            "7": ["7", "T"],
            "8": ["8", "B"],
            "9": ["9", "g", "q"],
            ":": [":", ";"],
        }
        if char in corruption_map:
            return random.choice(corruption_map[char])
    return char


def calculate_weird_time(t: float, duration: float) -> float:
    """Calculate display time with weird speed variations and reversals."""
    progress = t / duration

    # Base speed with dramatic variations
    speed_variation = 1.0 + 1.2 * math.sin(progress * math.pi * 3)

    # Long reverse zones (very noticeable)
    if 0.12 < progress < 0.22:
        speed_variation = -2.0
    elif 0.35 < progress < 0.45:
        speed_variation = -3.5
    elif 0.68 < progress < 0.75:
        speed_variation = -4.0
    # Dramatic slow motion zones
    elif 0.25 < progress < 0.32:
        speed_variation = 0.15
    elif 0.52 < progress < 0.58:
        speed_variation = 0.1
    # Hyper speed zones
    elif 0.60 < progress < 0.66:
        speed_variation = 5.0
    elif progress > 0.82:
        speed_variation = 6.0

    return speed_variation
