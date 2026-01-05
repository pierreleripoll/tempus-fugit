#!/usr/bin/env python3
"""Simple timer video generator."""

import os

# Force moviepy to use system ffmpeg (which has GPU support) - MUST be before importing moviepy
os.environ["FFMPEG_BINARY"] = "/usr/bin/ffmpeg"

from pathlib import Path
from moviepy.editor import VideoClip
import numpy as np
from PIL import Image, ImageDraw, ImageFont


# Configuration
RESOLUTION = (1920, 1080)
FPS = 5
BACKGROUND_COLOR = "black"
TEXT_COLOR = "red"
FONT_SIZE = 700
USE_GPU = True  # Enable GPU acceleration if available

# Timer settings
DISPLAY_DURATION = 150  # Time shown on the timer (seconds)
ACTUAL_DURATION = 150  # Actual video duration (seconds)
TIME_SCALE = DISPLAY_DURATION / ACTUAL_DURATION


def format_time(seconds: float) -> str:
    """Format seconds as MM:SS.cc (centiseconds)."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    centiseconds = int((seconds % 1) * 100)
    return f"{mins:02d}:{secs:02d}"


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

    def make_frame(t):
        """Generate a frame at time t."""
        # Calculate displayed time (counting down)
        visual_time = t * TIME_SCALE
        remaining_time = DISPLAY_DURATION - visual_time
        remaining_time = max(0, remaining_time)

        time_str = format_time(remaining_time)

        # Create image with PIL
        img = Image.new("RGB", RESOLUTION, color=BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)

        # Draw text centered (anchor='mm' means middle-middle)
        draw.text((center_x, center_y), time_str, font=font, fill=TEXT_COLOR, anchor="mm")

        return np.array(img)

    # Create video
    video = VideoClip(make_frame=make_frame, duration=ACTUAL_DURATION)
    video = video.set_fps(FPS)

    # Ensure output directory exists
    Path(output_path).parent.mkdir(exist_ok=True, parents=True)

    print(f"Generating timer video...")
    print(f"  Display duration: {DISPLAY_DURATION}s")
    print(f"  Actual duration: {ACTUAL_DURATION}s")
    print(f"  Time scale: {TIME_SCALE:.2f}x")
    print(f"  Resolution: {RESOLUTION[0]}x{RESOLUTION[1]}")
    print(f"  Output: {output_path}")

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
