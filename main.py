#!/usr/bin/env python3
"""Simple timer video generator."""

import os

# Force moviepy to use system ffmpeg (which has GPU support) - MUST be before importing moviepy
os.environ["FFMPEG_BINARY"] = "/usr/bin/ffmpeg"

from pathlib import Path
from moviepy.editor import VideoClip
import numpy as np
from PIL import Image, ImageDraw

from timer_utils import (
    RESOLUTION,
    BACKGROUND_COLOR,
    TEXT_COLOR,
    format_time,
    load_digital_font,
    get_codec_config,
)


# Configuration
FPS = 5

# Timer settings
DISPLAY_DURATION = 150  # Time shown on the timer (seconds)
ACTUAL_DURATION = 150  # Actual video duration (seconds)
TIME_SCALE = DISPLAY_DURATION / ACTUAL_DURATION


def generate_timer_video(output_path: str = "output/timer_test.mp4"):
    """Generate a countdown timer video."""

    font = load_digital_font()

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
    codec, ffmpeg_params = get_codec_config()

    try:
        video.write_videofile(
            output_path, fps=FPS, codec=codec, audio=False, ffmpeg_params=ffmpeg_params
        )
    except Exception as e:
        print(f"GPU encoding failed, falling back to CPU: {e}")
        codec, ffmpeg_params = get_codec_config(use_gpu=False)
        video.write_videofile(
            output_path,
            fps=FPS,
            codec=codec,
            audio=False,
            ffmpeg_params=ffmpeg_params,
        )

    print(f"✓ Video saved to {output_path}")


if __name__ == "__main__":
    generate_timer_video()
