#!/usr/bin/env python3
"""Weird festival timer video generator with glitch effects and animations."""

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
FPS = 25
BACKGROUND_COLOR = "black"
TEXT_COLOR = "red"
FONT_SIZE = 700
USE_GPU = True  # Enable GPU acceleration if available

# Timer settings
ACTUAL_DURATION = 120  # Actual video duration (seconds)


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


def animate_digit_wave(base_time_str: str, wave_progress: float) -> str:
    """Create wave animation through digits."""
    result = ""
    for i, char in enumerate(base_time_str):
        if char == ":":
            result += ":"
        else:
            phase = (wave_progress + i * 0.15) % 1.0
            if phase < 0.5:
                result += char
            else:
                result += " "
    return result


def animate_odd_even(base_time_str: str, anim_progress: float) -> str:
    """Animate odd digits appearing first, then even."""
    result = ""
    for i, char in enumerate(base_time_str):
        if char == ":":
            result += ":"
        elif anim_progress < 0.4:
            # Show nothing
            result += "8" if i % 2 == 1 else " "
        elif anim_progress < 0.7:
            # Show odd positions
            result += "8" if i % 2 == 1 else char
        else:
            # Show all
            result += char
    return result


def animate_segments_snake(t: float) -> str:
    """Animate using 7-segment display patterns like a snake/lightning."""
    patterns = [
        "-   -",
        "|-  -",
        "||  -",
        "||: -",
        "||:-|",
        "||:||",
        "-|:||",
        " -:||",
        "  :||",
        "  :-|",
        "  :- ",
    ]
    idx = int((t * 3) % len(patterns))
    return patterns[idx]


def animate_lightning(anim_progress: float, base_time_str: str) -> str:
    """Create lightning effect with vertical and horizontal bars."""
    if anim_progress < 0.2:
        return "  |  "
    elif anim_progress < 0.3:
        return " ||  "
    elif anim_progress < 0.4:
        return "|||  "
    elif anim_progress < 0.5:
        return "|||: "
    elif anim_progress < 0.6:
        return "|||:|"
    elif anim_progress < 0.8:
        return base_time_str
    else:
        # Flash
        return "88:88" if int(anim_progress * 20) % 2 == 0 else base_time_str


def animate_count_up(anim_progress: float) -> str:
    """Count up rapidly from 00:00."""
    seconds = int(anim_progress * 30)
    return format_time(seconds)


def animate_spinning_digits(anim_progress: float, base_time_str: str) -> str:
    """Each digit spins through numbers before settling."""
    result = ""
    for i, char in enumerate(base_time_str):
        if char == ":":
            result += ":"
        elif anim_progress < 0.7:
            # Spin through random numbers
            spin_speed = 10 + i * 2
            digit = int(anim_progress * spin_speed) % 10
            result += str(digit)
        else:
            # Settle to actual value
            result += char
    return result


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
    accumulated_time = [random.uniform(30, 180)]  # Start at random time!
    last_t = [0.0]

    # Track corruption state: {position: (corrupted_char, expiry_time)}
    corruption_state = {}

    # Track color state per character: {position: (color, expiry_time)}
    color_state = {}

    # Track animation states
    animation_mode = [None]
    animation_start_time = [0.0]
    animation_duration = [0.0]

    # Random jump schedule
    jump_times = sorted([random.uniform(5, ACTUAL_DURATION - 5) for _ in range(5)])
    jump_targets = [random.uniform(0, 250) for _ in range(5)]

    # Animation schedule - more frequent and starts earlier
    anim_times = sorted([random.uniform(3, ACTUAL_DURATION - 3) for _ in range(8)])

    def make_frame(t):
        """Generate a frame at time t with glitch effects."""
        progress = t / ACTUAL_DURATION

        # Random time jumps!
        for i, jump_t in enumerate(jump_times):
            if last_t[0] < jump_t <= t:
                accumulated_time[0] = jump_targets[i]
                print(f"  ⚡ Time jump at {t:.1f}s -> {format_time(jump_targets[i])}")

        # Trigger animations
        for i, anim_t in enumerate(anim_times):
            if last_t[0] < anim_t <= t and animation_mode[0] is None:
                modes = [
                    "wave",
                    "odd_even",
                    "all_eights",
                    "segments_snake",
                    "lightning",
                    "count_up",
                    "spinning",
                ]
                animation_mode[0] = random.choice(modes)
                animation_start_time[0] = t
                animation_duration[0] = random.uniform(2, 5)
                print(f"  🎬 Animation '{animation_mode[0]}' started at {t:.1f}s")

        # Check if animation expired
        if animation_mode[0] and (t - animation_start_time[0]) > animation_duration[0]:
            animation_mode[0] = None

        # Calculate weird time progression
        dt = t - last_t[0]
        last_t[0] = t

        speed = calculate_weird_time(t, ACTUAL_DURATION)
        accumulated_time[0] += dt * speed

        # Calculate displayed time (counting down)
        visual_time = accumulated_time[0]
        remaining_time = max(0, visual_time % 600)  # Wrap around at 10 minutes

        time_str = format_time(remaining_time)

        # Apply animations if active
        if animation_mode[0]:
            anim_progress = (t - animation_start_time[0]) / animation_duration[0]

            if animation_mode[0] == "wave":
                time_str = animate_digit_wave(time_str, anim_progress * 3)
            elif animation_mode[0] == "odd_even":
                time_str = animate_odd_even(time_str, anim_progress)
            elif animation_mode[0] == "all_eights":
                if anim_progress < 0.4:
                    time_str = "88:88"
                elif anim_progress < 0.7:
                    # Gradually reveal
                    reveal = int((anim_progress - 0.4) / 0.3 * len(time_str))
                    actual = format_time(remaining_time)
                    time_str = actual[:reveal] + "8" * (len(actual) - reveal)
            elif animation_mode[0] == "segments_snake":
                time_str = animate_segments_snake(t)
            elif animation_mode[0] == "lightning":
                time_str = animate_lightning(anim_progress, format_time(remaining_time))
            elif animation_mode[0] == "count_up":
                time_str = animate_count_up(anim_progress)
            elif animation_mode[0] == "spinning":
                time_str = animate_spinning_digits(anim_progress, format_time(remaining_time))

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

        # Get full text bbox
        full_bbox = draw.textbbox((center_x, center_y), corrupted_str, font=font, anchor="mm")
        full_width = full_bbox[2] - full_bbox[0]
        start_x = center_x - full_width // 2

        current_x = start_x
        for i, char in enumerate(corrupted_str):
            # Determine color for this character
            char_color = TEXT_COLOR

            # Check if this position has active color change
            if i in color_state and t < color_state[i][1]:
                char_color = color_state[i][0]
            elif random.random() > 0.998:  # 0.2% chance per character
                new_color = "magenta"
                duration = random.uniform(1.0, 3.0)
                color_state[i] = (new_color, t + duration)
                char_color = new_color

            # Draw this character (skip if space from animation)
            if char != " ":
                draw.text((current_x, center_y), char, font=font, fill=char_color, anchor="lm")

            # Move to next character position
            char_bbox = draw.textbbox((0, 0), char if char != " " else "0", font=font)
            char_width = char_bbox[2] - char_bbox[0]
            current_x += char_width

        return np.array(img)

    # Create video
    video = VideoClip(make_frame=make_frame, duration=ACTUAL_DURATION)
    video = video.set_fps(FPS)

    # Ensure output directory exists
    Path(output_path).parent.mkdir(exist_ok=True, parents=True)

    print(f"Generating FESTIVAL WEIRD timer video...")
    print(f"  Actual duration: {ACTUAL_DURATION}s")
    print(f"  Random time jumps: {len(jump_times)}")
    print(f"  Animations: {len(anim_times)}")
    print(f"  Resolution: {RESOLUTION[0]}x{RESOLUTION[1]}")
    print(f"  Output: {output_path}")
    print(f"  Effects: digit corruption, color glitches, speed variations, reversals, animations!")

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
