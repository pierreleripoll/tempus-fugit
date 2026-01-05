# Tempus Fugit - Timer Video Generator

Python project for generating creative countdown timer videos with various visual effects and animations.

## Features

Three timer generators with different styles:

- **main.py**: Clean, centered countdown timer with configurable durations
- **weird.py**: Timer with speed variations, reversals, and digit corruption glitches
- **festival.py**: Chaotic festival timer with animations, random time jumps, and color effects

### Effects Available

- Speed variations (slow motion, fast forward, reversals)
- Digit corruption and glitch effects
- Per-character color changes
- Animated transitions (wave, spinning, lightning, etc.)
- Random time jumps
- 7-segment display pattern animations

## Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
make install

# Or manually with uv
uv pip install -r requirements.txt
```

## Usage

### Quick Start

```bash
# Generate clean timer (2:30)
make main

# Generate weird timer with glitches (1:00)
make weird

# Generate festival timer with chaos (2:00)
make festival

# Run all generators
make all
```

### Manual Execution

```bash
# Clean timer
python main.py

# Weird glitchy timer
python weird.py

# Festival chaos timer
python festival.py
```

### Customization

Edit the configuration variables at the top of each file:

**main.py:**
- `DISPLAY_DURATION`: Time shown on timer (seconds)
- `ACTUAL_DURATION`: Actual video duration (seconds)
- `FPS`: Frames per second (5 recommended for simple timer)

**weird.py:**
- `DISPLAY_DURATION`: Time to count down from
- `ACTUAL_DURATION`: Real video length (60s default)
- Character corruption probability (0.3% default)
- Speed variation zones configured in `calculate_weird_time()`

**festival.py:**
- `ACTUAL_DURATION`: Video length (120s default)
- Number of time jumps (5 default)
- Number of animations (8 default)
- Color change probability (0.2% default)

## Project Structure

```
.
├── timer_utils.py         # Shared utilities (fonts, codec, effects)
├── main.py               # Clean countdown timer
├── weird.py              # Glitchy timer with speed variations
├── festival.py           # Festival timer with animations
├── output/               # Generated videos
├── requirements.txt
├── Makefile
└── README.md
```

## Output

Videos are saved to the `output/` directory as MP4 files:
- `output/timer_test.mp4` (from main.py)
- `output/timer_test.mp4` (from weird.py)
- `output/timer_test.mp4` (from festival.py)

## GPU Acceleration

The project supports AMD GPU acceleration via VAAPI. Falls back to CPU encoding automatically if GPU encoding fails.

To disable GPU:
- Set `USE_GPU = False` in `timer_utils.py`

## Font Requirements

For best results, install Digital-7 font:
- Download from: https://www.1001fonts.com/digital-7-font.html
- Install to `~/.fonts/` directory

The project will fall back to default fonts if Digital-7 is not found.

## Development

```bash
# Clean output directory
make clean

# Show available commands
make help
```

## Technical Details

- **Resolution**: 1920x1080 (Full HD)
- **Video Codec**: H.264 (GPU accelerated when available)
- **Frame Generation**: PIL for text rendering
- **Video Assembly**: MoviePy
- **Font Rendering**: Pillow (PIL)
