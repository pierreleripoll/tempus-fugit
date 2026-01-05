#!/usr/bin/env python3
"""Weird timer video generator with glitch effects."""

import os

# Force moviepy to use system ffmpeg (which has GPU support) - MUST be before importing moviepy
os.environ["FFMPEG_BINARY"] = "/usr/bin/ffmpeg"

from pathlib import Path
from moviepy.editor import VideoClip
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import math


# Configuration
RESOLUTION = (1920, 1080)
FPS = 20
BACKGROUND_COLOR = "black"
TEXT_COLOR = "red"
FONT_SIZE = 700
USE_GPU = True  # Enable GPU acceleration if available

# Timer settings
DISPLAY_DURATION = 60  # Time shown on the timer (seconds)
ACTUAL_DURATION = 60  # Actual video duration (seconds)
TIME_SCALE = DISPLAY_DURATION / ACTUAL_DURATION


def format_time(seconds: float) -> str:
    """Format seconds as MM:SS."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"


def corrupt_digit(char: str) -> str:
    """Randomly corrupt a digit to look glitchy."""
    if random.random() > 0.997:  # 0.3% chance of corruption
        corruption_map = {
            "0": [
                "O",
                "0",
                "D",
            ],
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
    # Create zones with different behaviors
    progress = t / duration

    # Base speed with dramatic variations
    speed_variation = 1.0 + 1.2 * math.sin(progress * math.pi * 3)

    # Long reverse zones (very noticeable)
    if 0.12 < progress < 0.22:  # 10% of video - long early reverse
        speed_variation = -2.0
    elif 0.35 < progress < 0.45:  # 10% of video - long mid reverse
        speed_variation = -3.5
    elif 0.68 < progress < 0.75:  # 7% of video - strong reverse
        speed_variation = -4.0

    # Dramatic slow motion zones
    elif 0.25 < progress < 0.32:  # 7% of video - super slow
        speed_variation = 0.15
    elif 0.52 < progress < 0.58:  # 6% of video - crawling speed
        speed_variation = 0.1

    # Hyper speed zones
    elif 0.60 < progress < 0.66:  # 6% of video - very fast
        speed_variation = 5.0
    elif progress > 0.82:  # Last 18% - extreme acceleration
        speed_variation = 6.0

    return speed_variation


def generate_timer_video(output_path: str = "output/timer_test.mp4"):
    """Generate a countdown timer video."""

    # Try to load a digital-style font (prioritize mono versions for consistent digit width)
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

    font = None
    for font_name in digital_fonts:
        try:
            font = ImageFont.truetype(font_name, FONT_SIZE)
            print(f"Using font: {font_name}")
            break
        except (OSError, IOError):
            continue

    if font is None:
        font = ImageFont.load_default()
        print("Warning: No digital font found. Install 'Digital-7' or similar for best results.")
        print("Download from: https://www.1001fonts.com/digital-7-font.html")

    # Calculate center position
    center_x = RESOLUTION[0] // 2
    center_y = RESOLUTION[1] // 2

    # Track accumulated time for weird time calculations
    accumulated_time = [0.0]
    last_t = [0.0]

    # Track corruption state: {position: (corrupted_char, expiry_time)}
    corruption_state = {}

    # Track color state per character: {position: (color, expiry_time)}
    color_state = {}

    def make_frame(t):
        """Generate a frame at time t with glitch effects."""
        # Calculate weird time progression
        dt = t - last_t[0]
        last_t[0] = t

        speed = calculate_weird_time(t, ACTUAL_DURATION)
        accumulated_time[0] += dt * speed

        # Calculate displayed time (counting down)
        visual_time = accumulated_time[0]
        remaining_time = DISPLAY_DURATION - visual_time
        remaining_time = max(0, min(DISPLAY_DURATION, remaining_time))

        time_str = format_time(remaining_time)

        # Apply persistent digit corruption
        corrupted_str = ""
        for i, char in enumerate(time_str):
            # Check if this position has active corruption
            if i in corruption_state and t < corruption_state[i][1]:
                # Use existing corruption
                corrupted_str += corruption_state[i][0]
            else:
                # Try to create new corruption
                corrupted_char = corrupt_digit(char)
                if corrupted_char != char:
                    # New corruption created, store it with expiry time
                    duration = random.uniform(0.3, 2.5)  # Last 0.3-2.5 seconds
                    corruption_state[i] = (corrupted_char, t + duration)
                    corrupted_str += corrupted_char
                else:
                    # No corruption
                    if i in corruption_state:
                        del corruption_state[i]
                    corrupted_str += char

        # Create image with PIL
        img = Image.new("RGB", RESOLUTION, color=BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)

        # Draw each character with individual color
        # Get text bounding box to position correctly
        full_bbox = draw.textbbox((0, 0), corrupted_str, font=font, anchor="mm")
        full_width = full_bbox[2] - full_bbox[0]
        start_x = center_x - full_width // 2

        current_x = start_x
        for i, char in enumerate(corrupted_str):
            # Determine color for this character
            char_color = TEXT_COLOR

            # Check if this position has active color change
            # if i in color_state and t < color_state[i][1]:
            #     char_color = color_state[i][0]
            # elif random.random() > 0.9995:  # 0.05% chance per character
            #     colors = ["red", "white", "yellow", "magenta"]
            #     new_color = random.choice(colors)
            #     duration = random.uniform(0.5, 1.5)  # Last 0.5-1.5 seconds
            #     color_state[i] = (new_color, t + duration)
            #     char_color = new_color

            # Draw this character
            draw.text((current_x, center_y), char, font=font, fill=char_color, anchor="lm")

            # Move to next character position
            char_bbox = draw.textbbox((0, 0), char, font=font)
            char_width = char_bbox[2] - char_bbox[0]
            current_x += char_width

        return np.array(img)

    # Create video
    video = VideoClip(make_frame=make_frame, duration=ACTUAL_DURATION)
    video = video.set_fps(FPS)

    # Ensure output directory exists
    Path(output_path).parent.mkdir(exist_ok=True, parents=True)

    print(f"Generating WEIRD timer video...")
    print(f"  Display duration: {DISPLAY_DURATION}s")
    print(f"  Actual duration: {ACTUAL_DURATION}s (real-time with glitches!)")
    print(f"  Resolution: {RESOLUTION[0]}x{RESOLUTION[1]}")
    print(f"  Output: {output_path}")
    print(f"  Effects: digit corruption, glitch lines, flickering, speed variations, reversals")

    # Configure codec based on GPU availability
    if USE_GPU:
        # AMD GPU using VAAPI
        os.environ["LIBVA_DRIVER_NAME"] = "radeonsi"

        codec = "h264_vaapi"
        # Initialize hardware device and use hwupload with device reference
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

    try:
        video.write_videofile(
            output_path, fps=FPS, codec=codec, audio=False, ffmpeg_params=ffmpeg_params
        )
    except Exception as e:
        if USE_GPU:
            print(f"GPU encoding failed, falling back to CPU: {e}")
            video.write_videofile(
                output_path,
                fps=FPS,
                codec="libx264",
                audio=False,
                ffmpeg_params=["-preset", "medium", "-crf", "23"],
            )
        else:
            raise

    print(f"✓ Video saved to {output_path}")


if __name__ == "__main__":
    generate_timer_video()
