# Timer GUI - User Guide

## For Your Non-Technical Friend! 👋

### Installation (One Time Only)

1. Open a terminal in this folder
2. Run: `uv pip install streamlit`
3. Done!

### How to Start the Interface

Just run this command:

```bash
uv run streamlit run timer_gui.py
```

Or use the Makefile shortcut:

```bash
make gui
```

A web browser will open automatically at `http://localhost:8501`

### Using the Interface

1. **Choose Timer Type** (left sidebar):

   - Jump Timer - For theatrical performances
   - Simple Timer - Clean and professional
   - Weird Timer - Glitchy effects
   - Festival Timer - Maximum chaos

2. **Adjust Settings** (sliders and numbers):

   - Display Duration: What time shows on timer (e.g., 150 = 2:30)
   - Actual Duration: How long the video file is
   - FPS: Higher = smoother (10-15 is fine)
   - Other settings change based on timer type

3. **Click "Generate Video"** button
   - Wait 1-5 minutes
   - Video appears in `output/` folder

### Tips

- **Start with defaults**: Just change one thing at a time
- **Test short videos**: Try 30-60 seconds first
- **Can't break anything**: Worst case, close and restart!

### Troubleshooting

**Browser doesn't open?**

- Manually go to: http://localhost:8501

**Error messages?**

- Try using the default values
- Check that durations are reasonable (30-300 seconds)

**Can't find video?**

- Look in the `output/` folder
- Check the filename you entered

### Stopping the Interface

Press `Ctrl+C` in the terminal window

---

**Need help?** Contact the person who gave you this! 😊
