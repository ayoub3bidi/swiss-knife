#!/usr/bin/env python3

import argparse
import json
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import mss

    HAS_MSS = True
except ImportError:
    HAS_MSS = False
    print("Error: mss not installed. Run: pip install mss")

try:
    from PIL import Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ScreenshotScheduler:
    def __init__(
        self,
        output_dir: Path,
        interval: int = 300,
        duration: Optional[int] = None,
        max_screenshots: Optional[int] = None,
        filename_pattern: str = "screenshot_{timestamp}.png",
        monitor: int = 0,
        quality: int = 85,
        resize: Optional[tuple] = None,
        format: str = "png",
    ):
        """
        Args:
            output_dir: Directory to save screenshots
            interval: Interval between screenshots in seconds
            duration: Total duration in seconds (None = run indefinitely)
            max_screenshots: Maximum number of screenshots to take
            filename_pattern: Filename pattern with {timestamp}, {counter} placeholders
            monitor: Monitor number to capture (0 = primary, -1 = all)
            quality: JPEG quality (1-100)
            resize: Tuple of (width, height) to resize screenshots
            format: Output format (png, jpg)
        """
        self.output_dir = Path(output_dir)
        self.interval = interval
        self.duration = duration
        self.max_screenshots = max_screenshots
        self.filename_pattern = filename_pattern
        self.monitor = monitor
        self.quality = quality
        self.resize = resize
        self.format = format.lower()

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.running = True
        self.screenshot_count = 0
        self.start_time = None
        self.total_size = 0

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        print("\n\nReceived interrupt signal. Stopping...")
        self.running = False

    def _format_filename(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.filename_pattern.replace("{timestamp}", timestamp)
        filename = filename.replace("{counter}", f"{self.screenshot_count:04d}")

        # Add extension if not present
        if not filename.endswith(f".{self.format}"):
            filename += f".{self.format}"

        return filename

    def _capture_screenshot(self) -> Optional[Path]:
        if not HAS_MSS:
            return None

        try:
            with mss.mss() as sct:
                # Get monitor
                if self.monitor == -1:
                    # Capture all monitors as one
                    monitor = sct.monitors[0]
                else:
                    monitor = sct.monitors[self.monitor + 1]

                # Capture
                screenshot = sct.grab(monitor)

                # Convert to PIL Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

                # Resize if requested
                if self.resize and HAS_PIL:
                    img = img.resize(self.resize, Image.Resampling.LANCZOS)

                # Generate filename
                filename = self._format_filename()
                filepath = self.output_dir / filename

                # Save
                if self.format == "jpg":
                    img.save(filepath, "JPEG", quality=self.quality, optimize=True)
                else:
                    img.save(filepath, "PNG", optimize=True)

                self.screenshot_count += 1
                self.total_size += filepath.stat().st_size

                return filepath

        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return None

    def _format_size(self, bytes_val: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} TB"

    def _format_duration(self, seconds: int) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0 or not parts:
            parts.append(f"{secs}s")

        return " ".join(parts)

    def _print_status(self, filepath: Path, elapsed: float):
        avg_size = (
            self.total_size / self.screenshot_count if self.screenshot_count > 0 else 0
        )

        status = f"[{self.screenshot_count:4d}] {filepath.name} ({self._format_size(filepath.stat().st_size)})"
        status += f" | Avg: {self._format_size(avg_size)}"
        status += f" | Elapsed: {self._format_duration(int(elapsed))}"

        if self.duration:
            remaining = self.duration - elapsed
            status += f" | Remaining: {self._format_duration(int(remaining))}"

        print(status)

    def run(self) -> None:
        print("=" * 80)
        print("SCREENSHOT SCHEDULER")
        print("=" * 80)
        print(f"Output directory: {self.output_dir}")
        print(f"Interval:         {self._format_duration(self.interval)}")
        print(
            f"Duration:         {'Unlimited' if not self.duration else self._format_duration(self.duration)}"
        )
        print(f"Max screenshots:  {self.max_screenshots or 'Unlimited'}")
        print(
            f"Monitor:          {'All' if self.monitor == -1 else f'#{self.monitor}'}"
        )
        print(f"Format:           {self.format.upper()}")
        if self.resize:
            print(f"Resize:           {self.resize[0]}x{self.resize[1]}")
        print("\nPress Ctrl+C to stop\n")

        self.start_time = time.time()
        next_capture = time.time()

        while self.running:
            current_time = time.time()
            elapsed = current_time - self.start_time

            # Check duration limit
            if self.duration and elapsed >= self.duration:
                print("\nDuration limit reached")
                break

            # Check max screenshots
            if self.max_screenshots and self.screenshot_count >= self.max_screenshots:
                print("\nMaximum screenshot count reached")
                break

            # Check if it's time for next capture
            if current_time >= next_capture:
                filepath = self._capture_screenshot()

                if filepath:
                    self._print_status(filepath, elapsed)

                next_capture = current_time + self.interval

            # Sleep briefly to avoid busy-waiting
            time.sleep(0.1)

        self._print_summary()

    def _print_summary(self):
        elapsed = time.time() - self.start_time if self.start_time else 0

        print("\n" + "=" * 80)
        print("SESSION SUMMARY")
        print("=" * 80)
        print(f"Screenshots taken:  {self.screenshot_count}")
        print(f"Total size:         {self._format_size(self.total_size)}")
        print(
            f"Average size:       {self._format_size(self.total_size / self.screenshot_count) if self.screenshot_count > 0 else '0 B'}"
        )
        print(f"Duration:           {self._format_duration(int(elapsed))}")
        print(f"Output directory:   {self.output_dir}")

        # Save metadata
        metadata = {
            "session": {
                "start_time": datetime.fromtimestamp(self.start_time).isoformat()
                if self.start_time
                else None,
                "end_time": datetime.now().isoformat(),
                "duration_seconds": int(elapsed),
                "interval_seconds": self.interval,
            },
            "statistics": {
                "total_screenshots": self.screenshot_count,
                "total_size_bytes": self.total_size,
                "average_size_bytes": self.total_size // self.screenshot_count
                if self.screenshot_count > 0
                else 0,
            },
            "settings": {
                "format": self.format,
                "quality": self.quality if self.format == "jpg" else None,
                "resize": f"{self.resize[0]}x{self.resize[1]}" if self.resize else None,
                "monitor": self.monitor,
            },
        }

        metadata_file = self.output_dir / "session_metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"Metadata saved:     {metadata_file}")


def parse_duration(duration_str: str) -> int:
    import re

    total_seconds = 0

    # Extract hours
    hours_match = re.search(r"(\d+)h", duration_str.lower())
    if hours_match:
        total_seconds += int(hours_match.group(1)) * 3600

    # Extract minutes
    minutes_match = re.search(r"(\d+)m", duration_str.lower())
    if minutes_match:
        total_seconds += int(minutes_match.group(1)) * 60

    # Extract seconds
    seconds_match = re.search(r"(\d+)s", duration_str.lower())
    if seconds_match:
        total_seconds += int(seconds_match.group(1))

    # If no units, assume seconds
    if not (hours_match or minutes_match or seconds_match):
        total_seconds = int(duration_str)

    return total_seconds


def main():

    parser = argparse.ArgumentParser(
        description="Automated screenshot scheduler for documentation and monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Take screenshot every 5 minutes indefinitely
  python screenshot_scheduler.py -o screenshots/ -i 5m

  # Take 100 screenshots every 30 seconds
  python screenshot_scheduler.py -o timelapse/ -i 30s --max 100

  # Run for 2 hours, screenshot every 10 minutes
  python screenshot_scheduler.py -o work_log/ -i 10m -d 2h

  # High-quality JPEGs, resized
  python screenshot_scheduler.py -o shots/ -i 1m --format jpg --quality 95 --resize 1920x1080

  # Capture all monitors
  python screenshot_scheduler.py -o multi/ -i 5m --monitor -1

Duration format: 1h30m, 30m, 90s, or just seconds
        """,
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output directory for screenshots",
    )

    parser.add_argument(
        "-i",
        "--interval",
        type=str,
        default="5m",
        help="Interval between screenshots (e.g., 5m, 30s, 1h) (default: 5m)",
    )
    parser.add_argument(
        "-d", "--duration", type=str, help="Total duration to run (e.g., 2h, 30m)"
    )
    parser.add_argument(
        "--max",
        "--max-screenshots",
        dest="max_screenshots",
        type=int,
        help="Maximum number of screenshots to take",
    )

    parser.add_argument(
        "--filename",
        type=str,
        default="screenshot_{timestamp}.png",
        help="Filename pattern (use {timestamp}, {counter})",
    )
    parser.add_argument(
        "--monitor",
        type=int,
        default=0,
        help="Monitor to capture (0=primary, -1=all) (default: 0)",
    )

    parser.add_argument(
        "--format",
        choices=["png", "jpg"],
        default="png",
        help="Output format (default: png)",
    )
    parser.add_argument(
        "--quality", type=int, default=85, help="JPEG quality 1-100 (default: 85)"
    )
    parser.add_argument(
        "--resize", type=str, help="Resize screenshots (e.g., 1920x1080)"
    )

    args = parser.parse_args()

    if not HAS_MSS:
        print("Error: mss library required. Install: pip install mss")
        sys.exit(1)

    if not HAS_PIL:
        print("Warning: Pillow not installed. Resize feature disabled.")
        print("Install: pip install Pillow")

    # Parse interval
    try:
        interval = parse_duration(args.interval)
        if interval < 1:
            print("Error: Interval must be at least 1 second")
            sys.exit(1)
    except Exception:
        print(f"Error: Invalid interval format: {args.interval}")
        sys.exit(1)

    # Parse duration
    duration = None
    if args.duration:
        try:
            duration = parse_duration(args.duration)
        except Exception:
            print(f"Error: Invalid duration format: {args.duration}")
            sys.exit(1)

    # Parse resize
    resize = None
    if args.resize:
        try:
            width, height = map(int, args.resize.split("x"))
            resize = (width, height)
        except Exception:
            print(f"Error: Invalid resize format: {args.resize}. Use WIDTHxHEIGHT")
            sys.exit(1)

    # Validate quality
    if not 1 <= args.quality <= 100:
        print("Error: Quality must be between 1 and 100")
        sys.exit(1)

    try:
        scheduler = ScreenshotScheduler(
            output_dir=args.output,
            interval=interval,
            duration=duration,
            max_screenshots=args.max_screenshots,
            filename_pattern=args.filename,
            monitor=args.monitor,
            quality=args.quality,
            resize=resize,
            format=args.format,
        )

        scheduler.run()

    except KeyboardInterrupt:
        print("\n\nStopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
