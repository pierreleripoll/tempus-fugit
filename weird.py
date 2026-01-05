#!/usr/bin/env python3
"""Weird timer video generator with glitch effects."""

import os

# Force moviepy to use system ffmpeg (which has GPU support) - MUST be before importing moviepy
os.environ["FFMPEG_BINARY"] = "/usr/bin/ffmpeg"

from pathlib import Path
from moviepy.editor import VideoClip
import numpy as np
from PIL import Image, ImageDraw
import random

from timer_utils import (
    RESOLUTION,
    BACKGROUND_COLOR,
    TEXT_COLOR,
    format_time,
    load_digital_font,
    get_codec_config,
    corrupt_digit,
    calculate_weird_time,
)


# Configuration
FPS = 20

# Timer settings
DISPLAY_DURATION = 60  # Time shown on the timer (seconds)
ACTUAL_DURATION = 60  # Actual video duration (seconds)
TIME_SCALE = DISPLAY_DURATION / ACTUAL_DURATION


def generate_timer_video(output_path: str = "output/timer_test.mp4"):
    """Generate a countdown timer video."""

    font = load_digital_font()

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
