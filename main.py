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
FPS = 15

# Timer settings
DISPLAY_DURATION = 150  # Time shown on the timer (seconds)
ACTUAL_DURATION = 110  # Actual video duration (seconds)
ACCELERATION_START = 0.6  # Start accelerating at this percentage (0.0-1.0)
USE_GRADUAL_ACCELERATION = True  # True = smooth acceleration, False = constant speed change

# Calculate acceleration automatically
# During normal phase: 1 second of video = 1 second on timer
# During acceleration phase: gradual acceleration using quadratic formula
# Formula: visual_time = v0*t + 0.5*a*t^2 (where v0=1.0, initial speed)
accel_start_time = ACCELERATION_START * ACTUAL_DURATION
normal_display_time = accel_start_time  # 1:1 ratio during normal phase
remaining_display_time = DISPLAY_DURATION - normal_display_time
remaining_actual_time = ACTUAL_DURATION - accel_start_time

# For gradual acceleration: solve for rate 'a' in s = v0*t + 0.5*a*t^2
ACCEL_RATE = (
    2 * (remaining_display_time - remaining_actual_time) / (remaining_actual_time**2)
    if remaining_actual_time > 0
    else 0.0
)

# For constant speed change: simple multiplier
ACCELERATION_FACTOR = (
    remaining_display_time / remaining_actual_time if remaining_actual_time > 0 else 1.0
)


def generate_timer_video(output_path: str = "output/timer_test.mp4"):
    """Generate a countdown timer video."""

    font = load_digital_font()

    # Calculate center position
    center_x = RESOLUTION[0] // 2
    center_y = RESOLUTION[1] // 2

    def make_frame(t):
        """Generate a frame at time t."""
        # Calculate displayed time (counting down) with acceleration
        accel_start_time = ACCELERATION_START * ACTUAL_DURATION

        if t <= accel_start_time:
            # Normal speed phase: 1 second of video = 1 second on timer
            visual_time = t
        else:
            # Acceleration phase
            normal_phase_display = accel_start_time  # Time counted during normal phase
            accel_phase_actual = t - accel_start_time  # Time elapsed in acceleration phase

            if USE_GRADUAL_ACCELERATION:
                # Gradual speed increase using kinematic equation: s = v0*t + 0.5*a*t^2
                accel_phase_display = (
                    1.0 * accel_phase_actual + 0.5 * ACCEL_RATE * accel_phase_actual**2
                )
            else:
                # Constant speed change
                accel_phase_display = accel_phase_actual * ACCELERATION_FACTOR

            visual_time = normal_phase_display + accel_phase_display

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
    print(f"  Normal phase: {accel_start_time:.1f}s (1:1 speed)")

    if USE_GRADUAL_ACCELERATION:
        # Calculate final speed (v = v0 + a*t)
        final_speed = 1.0 + ACCEL_RATE * remaining_actual_time
        print(
            f"  Acceleration phase: {ACTUAL_DURATION - accel_start_time:.1f}s (1.0x → {final_speed:.2f}x)"
        )
    else:
        print(
            f"  Acceleration phase: {ACTUAL_DURATION - accel_start_time:.1f}s ({ACCELERATION_FACTOR:.2f}x constant)"
        )

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
