#!/usr/bin/env python3
"""Streamlit GUI for timer video generation - No coding required!"""

import streamlit as st
import subprocess
import sys
from pathlib import Path
import tempfile
import shutil

st.set_page_config(page_title="Timer Video Generator", page_icon="⏱", layout="wide")

st.title("Timer Video Generator")
st.markdown("### Easy interface to create custom timer videos")

# Sidebar for timer type selection
st.sidebar.header("Choose Timer Type")
timer_type = st.sidebar.radio(
    "Select which timer to generate:",
    [
        "Jump Timer (Theatrical)",
        "Simple Timer",
        "Weird Timer (Glitchy)",
        "Festival Timer (Chaotic)",
    ],
    help="Each timer has different visual effects",
)

# Main content area with tabs
tab1, tab2, tab3 = st.tabs(["Settings", "About", "Instructions"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Time Settings")

        display_duration = st.number_input(
            "Display Duration (seconds)",
            min_value=10,
            max_value=600,
            value=150,
            step=10,
            help="How much time to show on the timer (e.g., 150 = 2:30)",
        )

        actual_duration = st.number_input(
            "Actual Video Duration (seconds)",
            min_value=10,
            max_value=600,
            value=110,
            step=10,
            help="How long the video file will be",
        )

        st.subheader("Video Settings")

        fps = st.slider(
            "FPS (Frames Per Second)",
            min_value=5,
            max_value=30,
            value=15,
            step=1,
            help="Higher = smoother but larger file size",
        )

        output_name = st.text_input(
            "Output Filename", value="timer", help="Name for the output file (without .mp4)"
        )

    with col2:
        # Show different settings based on timer type
        if "Jump" in timer_type:
            st.subheader("Jump Settings")

            jump_start = st.slider(
                "Jump Position (%)",
                min_value=0.0,
                max_value=1.0,
                value=0.6,
                step=0.05,
                help="When the time jump happens (0.6 = 60% through video)",
            )

            jump_amount = st.slider(
                "Jump Amount (seconds)",
                min_value=5,
                max_value=60,
                value=15,
                step=5,
                help="How many seconds to skip forward",
            )

            glitch_before_jump = st.slider(
                "Glitch Warning (seconds)",
                min_value=0.5,
                max_value=5.0,
                value=2.0,
                step=0.5,
                help="How long before jump to start glitching",
            )

        elif "Simple" in timer_type:
            st.subheader("Speed Settings")

            acceleration_start = st.slider(
                "Acceleration Start (%)",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.05,
                help="When to start speeding up",
            )

            use_gradual = st.checkbox(
                "Use Gradual Acceleration",
                value=True,
                help="If unchecked, uses constant speed change",
            )

        elif "Weird" in timer_type:
            st.subheader("Weird Settings")
            st.info("Weird timer has preset glitch effects and speed variations")

        elif "Festival" in timer_type:
            st.subheader("Festival Settings")
            st.info("Festival timer has random jumps and animations built-in")

    st.divider()

    # Generate button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

    with col_btn2:
        generate_button = st.button("Generate Video", type="primary", use_container_width=True)

with tab2:
    st.markdown(
        """
    ## About Timer Types
    
    ### Jump Timer (Theatrical)
    Perfect for live performances! The timer:
    - Runs normally for the first part
    - Starts glitching as a warning
    - Suddenly jumps forward (skips time)
    - Runs faster after the jump
    
    **Use case:** Creates stress and urgency for actors on stage
    
    ### Simple Timer
    Clean countdown with optional acceleration:
    - Normal countdown at 1:1 speed
    - Can accelerate smoothly or jump to faster speed
    - Professional and clear to read
    
    **Use case:** Presentations, rehearsals, simple timing needs
    
    ### Weird Timer
    Glitchy artistic timer with:
    - Random digit corruptions
    - Speed variations and reversals
    - Unpredictable time flow
    
    **Use case:** Experimental performances, art installations
    
    ### Festival Timer
    Chaotic timer with everything:
    - Random time jumps
    - Multiple animation modes
    - Color glitches
    - Speed changes
    
    **Use case:** Festival vibes, maximum chaos
    """
    )

with tab3:
    st.markdown(
        """
    ## How to Use
    
    ### For Complete Beginners:
    
    1. **Choose a timer type** from the sidebar (left)
    2. **Adjust the numbers** using the sliders and input boxes
    3. **Click "Generate Video"** button
    4. **Wait** - it will take 1-5 minutes depending on settings
    5. **Find your video** in the `output/` folder
    
    ### Tips:
    
    - **Start simple**: Use default values first, then experiment
    - **Higher FPS = bigger files**: Use 10-15 FPS for most cases
    - **Test short videos first**: Try 30-60 seconds before making long ones
    - **Jump Timer tips**: 
      - Jump Position 0.6 = jump happens 60% through
      - Jump Amount 15 = skips 15 seconds
      - Glitch Warning 2.0 = starts glitching 2 seconds before
    
    ### Getting Help:
    
    If something doesn't work:
    1. Check the error message in red text
    2. Try using default values
    3. Make sure "Display Duration" is reasonable (30-300 seconds)
    4. Contact your friendly neighborhood developer!
    """
    )

# Handle generation
if generate_button:
    # Validate settings
    if actual_duration <= 0 or display_duration <= 0:
        st.error("Duration values must be positive!")
    else:
        # Create a temporary Python file with the settings
        output_path = f"output/{output_name}.mp4"

        with st.spinner(f"Generating {timer_type}... This may take a few minutes..."):
            try:
                # Determine which script to modify and run
                if "Jump" in timer_type:
                    # Create temporary modified jump.py
                    script_content = f"""#!/usr/bin/env python3
import os
os.environ["FFMPEG_BINARY"] = "/usr/bin/ffmpeg"
import sys
sys.path.insert(0, '{Path(__file__).parent.absolute()}')

# Override settings
FPS = {fps}
DISPLAY_DURATION = {display_duration}
ACTUAL_DURATION = {actual_duration}
JUMP_START = {jump_start}
JUMP_AMOUNT = {jump_amount}
GLITCH_BEFORE_JUMP = {glitch_before_jump}
OUTPUT_PATH = "{output_path}"

# Import and patch jump module
import jump
jump.FPS = FPS
jump.DISPLAY_DURATION = DISPLAY_DURATION
jump.ACTUAL_DURATION = ACTUAL_DURATION
jump.JUMP_START = JUMP_START
jump.JUMP_AMOUNT = JUMP_AMOUNT
jump.GLITCH_BEFORE_JUMP = GLITCH_BEFORE_JUMP

# Recalculate derived values
jump.jump_time = JUMP_START * ACTUAL_DURATION
jump.normal_display_time = jump.jump_time
jump.remaining_display_time = DISPLAY_DURATION - jump.normal_display_time - JUMP_AMOUNT
jump.remaining_actual_time = ACTUAL_DURATION - jump.jump_time
jump.RUSH_FACTOR = jump.remaining_display_time / jump.remaining_actual_time if jump.remaining_actual_time > 0 else 1.0

jump.generate_timer_video(OUTPUT_PATH)
"""

                elif "Simple" in timer_type:
                    script_content = f"""#!/usr/bin/env python3
import os
os.environ["FFMPEG_BINARY"] = "/usr/bin/ffmpeg"
import sys
sys.path.insert(0, '{Path(__file__).parent.absolute()}')

FPS = {fps}
DISPLAY_DURATION = {display_duration}
ACTUAL_DURATION = {actual_duration}
ACCELERATION_START = {acceleration_start}
USE_GRADUAL_ACCELERATION = {use_gradual}
OUTPUT_PATH = "{output_path}"

import main
main.FPS = FPS
main.DISPLAY_DURATION = DISPLAY_DURATION
main.ACTUAL_DURATION = ACTUAL_DURATION
main.ACCELERATION_START = ACCELERATION_START
main.USE_GRADUAL_ACCELERATION = USE_GRADUAL_ACCELERATION

# Recalculate
main.accel_start_time = ACCELERATION_START * ACTUAL_DURATION
main.normal_display_time = main.accel_start_time
main.remaining_display_time = DISPLAY_DURATION - main.normal_display_time
main.remaining_actual_time = ACTUAL_DURATION - main.accel_start_time
main.ACCEL_RATE = (
    2 * (main.remaining_display_time - main.remaining_actual_time) / (main.remaining_actual_time**2)
    if main.remaining_actual_time > 0 else 0.0
)
main.ACCELERATION_FACTOR = (
    main.remaining_display_time / main.remaining_actual_time if main.remaining_actual_time > 0 else 1.0
)

main.generate_timer_video(OUTPUT_PATH)
"""

                elif "Weird" in timer_type:
                    script_content = f"""#!/usr/bin/env python3
import os
os.environ["FFMPEG_BINARY"] = "/usr/bin/ffmpeg"
import sys
sys.path.insert(0, '{Path(__file__).parent.absolute()}')

FPS = {fps}
DISPLAY_DURATION = {display_duration}
ACTUAL_DURATION = {actual_duration}
OUTPUT_PATH = "{output_path}"

import weird
weird.FPS = FPS
weird.DISPLAY_DURATION = DISPLAY_DURATION
weird.ACTUAL_DURATION = ACTUAL_DURATION

weird.generate_timer_video(OUTPUT_PATH)
"""

                else:  # Festival
                    script_content = f"""#!/usr/bin/env python3
import os
os.environ["FFMPEG_BINARY"] = "/usr/bin/ffmpeg"
import sys
sys.path.insert(0, '{Path(__file__).parent.absolute()}')

FPS = {fps}
ACTUAL_DURATION = {actual_duration}
OUTPUT_PATH = "{output_path}"

import festival
festival.FPS = FPS
festival.ACTUAL_DURATION = ACTUAL_DURATION

festival.generate_timer_video(OUTPUT_PATH)
"""

                # Write temporary script
                temp_script = Path(tempfile.gettempdir()) / "temp_timer_script.py"
                temp_script.write_text(script_content)

                # Run it
                result = subprocess.run(
                    [sys.executable, str(temp_script)],
                    capture_output=True,
                    text=True,
                    cwd=Path(__file__).parent,
                )

                # Clean up
                temp_script.unlink()

                if result.returncode == 0:
                    st.success(f"Video generated successfully!")
                    st.info(f"Saved to: `{output_path}`")

                    # Preview the video
                    st.subheader("Preview")
                    if Path(output_path).exists():
                        st.video(output_path)

                        # Download button
                        with open(output_path, "rb") as video_file:
                            st.download_button(
                                label="Download Video",
                                data=video_file,
                                file_name=f"{output_name}.mp4",
                                mime="video/mp4",
                                use_container_width=True,
                            )
                    else:
                        st.warning("Video file not found. Check the output path.")

                    # Show details
                    with st.expander("Generation Details"):
                        st.code(result.stdout)
                else:
                    st.error(f"Generation failed!")
                    st.code(result.stderr)

            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.divider()
st.markdown(
    """
<div style='text-align: center; color: #666;'>
    <p>Timer Video Generator | Made with Streamlit</p>
    <p><small>No coding skills required - just adjust sliders and click generate!</small></p>
</div>
""",
    unsafe_allow_html=True,
)
