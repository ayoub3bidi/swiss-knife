# Automation Tools

Scripts for automating repetitive tasks and scheduled operations.

## Available Scripts

### 📸 Desktop Screenshot Scheduler (`screenshot_scheduler.py`)
Automatically capture screenshots at specified intervals for documentation, monitoring, or timelapse creation.

**Features:**
- Scheduled screenshot capture at custom intervals
- Duration and max screenshot limits
- Multi-monitor support (capture specific or all monitors)
- Format options (PNG, JPEG with quality control)
- Automatic resizing for smaller file sizes
- Session metadata tracking
- Graceful interrupt handling
- Customizable filename patterns

**Usage:**
```bash
# Every 5 minutes indefinitely
python screenshot_scheduler.py -o screenshots/ -i 5m

# 100 screenshots every 30 seconds
python screenshot_scheduler.py -o timelapse/ -i 30s --max 100

# Run for 2 hours, every 10 minutes
python screenshot_scheduler.py -o work_log/ -i 10m -d 2h

# High-quality JPEGs, resized
python screenshot_scheduler.py -o shots/ -i 1m --format jpg --quality 95 --resize 1920x1080

# Capture all monitors
python screenshot_scheduler.py -o multi/ -i 5m --monitor -1
```

**Real-World Scenarios:**

**Time Tracking:**
```bash
# Capture every 10 minutes during work hours
python screenshot_scheduler.py -o ~/work_log/ -i 10m -d 8h
```

**Documentation:**
```bash
# Capture during tutorial recording
python screenshot_scheduler.py -o tutorial_frames/ -i 30s -d 1h --resize 1280x720
```

**Timelapse Creation:**
```bash
# Capture every 5 seconds for 2 minutes
python screenshot_scheduler.py -o timelapse/ -i 5s -d 2m --max 24

# Convert to video (requires ffmpeg)
ffmpeg -framerate 12 -pattern_type glob -i 'timelapse/*.png' -c:v libx264 timelapse.mp4
```

**Security Monitoring:**
```bash
# Low-quality, long duration
python screenshot_scheduler.py -o monitor/ -i 5m -d 24h --format jpg --quality 60
```

**Session Metadata:**
Each session creates `session_metadata.json` with:
- Start/end times
- Duration and interval
- Screenshot count and sizes
- Format settings

## Installation
```bash
pip install -r automation/requirements.txt
```

## Coming Soon
- ✅ Desktop screenshot scheduler (COMPLETED)
- [ ] Database backup automator
- [ ] Email sender with templates
- [ ] Calendar event creator from CSV
- [ ] Password generator with policies
