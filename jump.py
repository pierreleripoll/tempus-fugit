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
    corrupt_digit,
)


# Configuration
FPS = 15

# Timer settings
DISPLAY_DURATION = 150  # Time shown on the timer (seconds)
ACTUAL_DURATION = 130  # Actual video duration (seconds)
JUMP_START = 0.8  # When the time jump happens (0.0-1.0)
JUMP_AMOUNT = 15  # How many seconds to skip forward instantly
GLITCH_BEFORE_JUMP = 5  # Start glitching this many seconds before jump

# Calculate rush phase speed automatically
# Normal phase: 1 second of video = 1 second on timer (1:1)
# At JUMP_START: Timer suddenly jumps forward by JUMP_AMOUNT seconds
# Rush phase: Timer runs faster to reach the end at ACTUAL_DURATION
jump_time = JUMP_START * ACTUAL_DURATION
normal_display_time = jump_time  # Time counted during normal phase
remaining_display_time = DISPLAY_DURATION - normal_display_time - JUMP_AMOUNT
remaining_actual_time = ACTUAL_DURATION - jump_time

# Calculate rush speed factor
RUSH_FACTOR = remaining_display_time / remaining_actual_time if remaining_actual_time > 0 else 1.0


def generate_timer_video(output_path: str = "output/jump.mp4"):
    """Generate a countdown timer video."""

    font = load_digital_font()

    # Calculate center position
    center_x = RESOLUTION[0] // 2
    center_y = RESOLUTION[1] // 2

    # Track corruption state: {position: (corrupted_char, expiry_time)}
    corruption_state = {}

    def make_frame(t):
        """Generate a frame at time t."""
        # Calculate displayed time with jump effect
        jump_time = JUMP_START * ACTUAL_DURATION
        glitch_start = jump_time - GLITCH_BEFORE_JUMP

        if t < jump_time:
            # Normal speed phase: 1 second of video = 1 second on timer
            visual_time = t
        else:
            # Rush phase after the jump
            normal_phase_display = jump_time  # Time counted during normal phase
            rush_phase_actual = t - jump_time  # Time elapsed in rush phase
            rush_phase_display = rush_phase_actual * RUSH_FACTOR  # Time counted during rush

            # Add the instant jump
            visual_time = normal_phase_display + JUMP_AMOUNT + rush_phase_display

        remaining_time = DISPLAY_DURATION - visual_time
        remaining_time = max(0, remaining_time)

        time_str = format_time(remaining_time)

        # Apply glitch effect right before the jump with persistent corruption
        if glitch_start <= t < jump_time:
            # Calculate how close we are to the jump (0.0 at start, 1.0 at jump)
            glitch_intensity = (t - glitch_start) / GLITCH_BEFORE_JUMP

            # Increase corruption chance as we get closer to jump
            # Start at 99.5% chance (very rare), end at 90% chance (more frequent)
            corruption_chance = 0.995 - (glitch_intensity * 0.095)

            # Apply persistent corruption to each character
            glitched_str = ""
            for i, char in enumerate(time_str):
                # Check if this position has active corruption
                if i in corruption_state and t < corruption_state[i][1]:
                    # Use existing corruption
                    glitched_str += corruption_state[i][0]
                else:
                    # Try to create new corruption
                    corrupted_char = corrupt_digit(char, corruption_chance)
                    if corrupted_char != char:
                        # New corruption created, store it with expiry time
                        # Duration increases as we approach the jump (0.3s to 1.0s)
                        duration = 0.3 + (glitch_intensity * 0.7)
                        corruption_state[i] = (corrupted_char, t + duration)
                        glitched_str += corrupted_char
                    else:
                        # No corruption
                        if i in corruption_state:
                            del corruption_state[i]
                        glitched_str += char
            time_str = glitched_str
        else:
            # Clear corruption state when not in glitch zone
            corruption_state.clear()
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
    print(f"  Normal phase: {jump_time:.1f}s (1:1 speed)")
    print(f"  Glitch warning: {GLITCH_BEFORE_JUMP}s before jump")
    print(f"  Jump: -{JUMP_AMOUNT}s instantly at {jump_time:.1f}s mark")
    print(f"  Rush phase: {ACTUAL_DURATION - jump_time:.1f}s ({RUSH_FACTOR:.2f}x speed)")
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
