# Automation Tools

Scripts for automating repetitive tasks and scheduled operations.

## Available Scripts

### Desktop Screenshot Scheduler (`screenshot_scheduler.py`)
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

### Password Generator (`password_generator.py`)
Generate cryptographically secure passwords with customizable policies and strength analysis.

**Features:**
- Cryptographically secure (uses `secrets` module)
- Customizable length and character requirements
- Policy enforcement (min uppercase/lowercase/digits/special)
- Exclude ambiguous/similar characters
- Pattern detection (repeating, sequential, common words)
- Passphrase generation (memorable)
- Strength analysis with entropy calculation
- Batch generation
- JSON export

**Usage:**
```bash
# Generate single password (16 chars)
python password_generator.py

# 20-character password
python password_generator.py -l 20

# Generate 10 passwords
python password_generator.py -n 10

# Strict policy
python password_generator.py -l 16 --no-ambiguous --no-repeating --no-sequential

# Custom requirements
python password_generator.py -l 20 --min-upper 2 --min-lower 2 --min-digits 3 --min-special 3

# Passphrase (memorable)
python password_generator.py --passphrase -w 5

# Analyze existing password
python password_generator.py --analyze "MyP@ssw0rd123"

# JSON output with strength
python password_generator.py -n 5 --show-strength --json
```

**Strength Levels:**
- **Excellent** (90-100): Very strong, resistant to attacks
- **Strong** (70-89): Good security, recommended
- **Good** (50-69): Acceptable for most uses
- **Fair** (30-49): Weak, consider stronger
- **Weak** (<30): Not recommended

**No Dependencies:** Uses only Python standard library.

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

