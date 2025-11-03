# System Utilities
A collection of system monitoring and management tools for tracking resource usage, managing processes, and maintaining system health.

## Available Scripts

### 🖥️ System Resource Monitor (`system_monitor.py`)
Real-time system resource monitoring with configurable thresholds and intelligent alerting.

**Features:**
- Real-time CPU, memory, disk, and network monitoring
- Configurable alert thresholds with cooldown periods
- Historical trending and statistics
- Top process tracking by CPU/memory usage
- Continuous monitoring with periodic checks
- JSON logging for analysis
- Detailed reporting and export
- Single-check mode for quick status
- Cross-platform support (Linux, macOS, Windows)

## Installation
```bash
# Install dependencies
pip install -r system_utilities/requirements.txt

# Verify installation
python -c "import psutil; print('psutil version:', psutil.__version__)"
```

## Quick Start

### Basic Monitoring
```bash
# Start monitoring with default thresholds
python system_utilities/system_monitor.py

# Single status check
python system_utilities/system_monitor.py --once

# Monitor for 5 minutes
python system_utilities/system_monitor.py --duration 300

# Show top processes
python system_utilities/system_monitor.py --show-processes
```

### Custom Thresholds
```bash
# Strict monitoring
python system_utilities/system_monitor.py --cpu-threshold 60 --memory-threshold 70

# Relaxed monitoring for servers
python system_utilities/system_monitor.py --cpu-threshold 90 --memory-threshold 95 --disk-threshold 95

# Network-focused monitoring
python system_utilities/system_monitor.py --network-threshold 50 --interval 2
```

### Logging and Reporting
```bash
# Enable logging
python system_utilities/system_monitor.py --log /var/log/system_monitor.log

# Export detailed report
python system_utilities/system_monitor.py --duration 3600 --export-report report.json

# Continuous monitoring with logging
python system_utilities/system_monitor.py --log monitor.log --interval 10
```

## Usage Examples

### System Resource Monitor

#### Production Server Monitoring
```bash
# Monitor server with appropriate thresholds
python system_utilities/system_monitor.py \
  --cpu-threshold 85 \
  --memory-threshold 90 \
  --disk-threshold 95 \
  --interval 10 \
  --log /var/log/monitor.log
```

#### Development Workstation
```bash
# Monitor with more frequent checks
python system_utilities/system_monitor.py \
  --cpu-threshold 70 \
  --memory-threshold 80 \
  --show-processes \
  --interval 3
```

#### Quick Health Check
```bash
# Single check with process info
python system_utilities/system_monitor.py --once --show-processes

# Get JSON report for automation
python system_utilities/system_monitor.py --once --export-report health.json
```

```bash
# Safe preview
python system_utilities/process_killer.py --min-memory 2048 --dry-run

# Kill Chrome tabs using >500MB
python system_utilities/process_killer.py --name chrome --min-memory 500

# Kill high memory processes, protect database
python system_utilities/process_killer.py --memory-threshold 85 --exclude-user postgres

# Emergency: Kill top memory consumers immediately
python system_utilities/process_killer.py --min-memory 1024 --force
```

### 💾 Disk Space Analyzer (`disk_analyzer.py`)
Analyze directory sizes and visualize space usage with detailed breakdowns.

**Usage:**
```bash
# Analyze directory
python system_utilities/disk_analyzer.py ~/Documents

# Export report
python system_utilities/disk_analyzer.py /var/log --export report.json

# Limit depth and size
python system_utilities/disk_analyzer.py ~ --max-depth 3 --min-size 100MB
```

**Makefile target:**
```makefile
disk-demo: ## Show disk analyzer examples
	@echo "  Analyze directory:  python system_utilities/disk_analyzer.py ~/Documents"
	@echo "  Find space hogs:    python system_utilities/disk_analyzer.py /var --min-size 100MB"
```

This completes the system utilities section nicely. Ready to move to the next category? The Development Tools section has some interesting ones like "Code formatter for multiple languages" or we could jump to Network/Web tools.

