import argparse
import json
import sys
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Error: psutil not installed. Run: pip install psutil")
    sys.exit(1)

try:
    from tqdm import tqdm  # noqa: F401

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class AlertManager:
    def __init__(self, cooldown_seconds: int = 300):
        self.cooldown_seconds = cooldown_seconds
        self.last_alert_time: Dict[str, float] = {}
        self.alert_history: List[Dict] = []
        self.alert_count: Dict[str, int] = {}

    def should_alert(self, alert_type: str) -> bool:
        current_time = time.time()
        last_time = self.last_alert_time.get(alert_type, 0)
        return (current_time - last_time) >= self.cooldown_seconds

    def record_alert(self, alert_type: str, message: str, severity: str, details: Dict):
        self.last_alert_time[alert_type] = time.time()
        self.alert_count[alert_type] = self.alert_count.get(alert_type, 0) + 1

        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "severity": severity,
            "message": message,
            "details": details,
            "count": self.alert_count[alert_type],
        }
        self.alert_history.append(alert)
        return alert

    def get_stats(self) -> Dict:
        return {
            "total_alerts": len(self.alert_history),
            "alerts_by_type": dict(self.alert_count),
            "recent_alerts": self.alert_history[-10:] if self.alert_history else [],
        }


class ResourceMonitor:
    def __init__(
        self,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 85.0,
        disk_threshold: float = 90.0,
        network_threshold: float = 100.0,  # MB/s
        check_interval: int = 5,
        alert_cooldown: int = 300,
        log_file: Optional[str] = None,
    ):
        self.thresholds = {
            "cpu": cpu_threshold,
            "memory": memory_threshold,
            "disk": disk_threshold,
            "network": network_threshold,
        }

        self.check_interval = check_interval
        self.alert_manager = AlertManager(alert_cooldown)
        self.log_file = Path(log_file) if log_file else None

        # Historical data for trending
        self.history = {
            "cpu": deque(maxlen=60),
            "memory": deque(maxlen=60),
            "disk": deque(maxlen=60),
            "network_sent": deque(maxlen=60),
            "network_recv": deque(maxlen=60),
        }

        # Network baseline
        self.last_network = psutil.net_io_counters()
        self.last_network_time = time.time()

        self.running = True
        self.stats = {
            "checks_performed": 0,
            "alerts_triggered": 0,
            "start_time": datetime.now().isoformat(),
        }

    def _format_bytes(self, bytes_val: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_val < 1024:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.2f} PB"

    def _get_cpu_info(self) -> Dict:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)

        cpu_freq = psutil.cpu_freq()
        freq_info = {
            "current": cpu_freq.current if cpu_freq else 0,
            "min": cpu_freq.min if cpu_freq else 0,
            "max": cpu_freq.max if cpu_freq else 0,
        }

        load_avg = psutil.getloadavg() if hasattr(psutil, "getloadavg") else (0, 0, 0)

        return {
            "percent": cpu_percent,
            "count": cpu_count,
            "per_cpu": per_cpu,
            "frequency": freq_info,
            "load_average": {
                "1min": load_avg[0],
                "5min": load_avg[1],
                "15min": load_avg[2],
            },
        }

    def _get_memory_info(self) -> Dict:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            "percent": mem.percent,
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "free": mem.free,
            "swap_percent": swap.percent,
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_free": swap.free,
        }

    def _get_disk_info(self) -> Dict:
        disks = {}

        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks[partition.mountpoint] = {
                    "device": partition.device,
                    "fstype": partition.fstype,
                    "percent": usage.percent,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                }
            except (PermissionError, OSError):
                continue

        # Disk I/O stats
        disk_io = psutil.disk_io_counters()
        io_stats = (
            {
                "read_bytes": disk_io.read_bytes,
                "write_bytes": disk_io.write_bytes,
                "read_count": disk_io.read_count,
                "write_count": disk_io.write_count,
            }
            if disk_io
            else {}
        )

        return {"partitions": disks, "io_stats": io_stats}

    def _get_network_info(self) -> Dict:
        current_net = psutil.net_io_counters()
        current_time = time.time()

        time_delta = current_time - self.last_network_time

        if time_delta > 0:
            bytes_sent_per_sec = (
                current_net.bytes_sent - self.last_network.bytes_sent
            ) / time_delta
            bytes_recv_per_sec = (
                current_net.bytes_recv - self.last_network.bytes_recv
            ) / time_delta
        else:
            bytes_sent_per_sec = 0
            bytes_recv_per_sec = 0

        self.last_network = current_net
        self.last_network_time = current_time

        # Network connections
        connections = psutil.net_connections(kind="inet")
        connection_stats = {
            "total": len(connections),
            "established": len([c for c in connections if c.status == "ESTABLISHED"]),
            "listen": len([c for c in connections if c.status == "LISTEN"]),
        }

        return {
            "bytes_sent": current_net.bytes_sent,
            "bytes_recv": current_net.bytes_recv,
            "packets_sent": current_net.packets_sent,
            "packets_recv": current_net.packets_recv,
            "errin": current_net.errin,
            "errout": current_net.errout,
            "dropin": current_net.dropin,
            "dropout": current_net.dropout,
            "speed_sent_mbps": bytes_sent_per_sec / (1024 * 1024),
            "speed_recv_mbps": bytes_recv_per_sec / (1024 * 1024),
            "connections": connection_stats,
        }

    def _get_process_info(self, limit: int = 5) -> List[Dict]:
        processes = []

        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent", "username"]
        ):
            try:
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage
        top_cpu = sorted(processes, key=lambda p: p["cpu_percent"] or 0, reverse=True)[
            :limit
        ]

        # Sort by memory usage
        top_mem = sorted(
            processes, key=lambda p: p["memory_percent"] or 0, reverse=True
        )[:limit]

        return {"top_cpu": top_cpu, "top_memory": top_mem}

    def check_resources(self) -> Dict:
        self.stats["checks_performed"] += 1

        cpu_info = self._get_cpu_info()
        memory_info = self._get_memory_info()
        disk_info = self._get_disk_info()
        network_info = self._get_network_info()

        # Update history
        self.history["cpu"].append(cpu_info["percent"])
        self.history["memory"].append(memory_info["percent"])

        # Get average disk usage across all partitions
        if disk_info["partitions"]:
            avg_disk = sum(
                p["percent"] for p in disk_info["partitions"].values()
            ) / len(disk_info["partitions"])
            self.history["disk"].append(avg_disk)

        self.history["network_sent"].append(network_info["speed_sent_mbps"])
        self.history["network_recv"].append(network_info["speed_recv_mbps"])

        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": cpu_info,
            "memory": memory_info,
            "disk": disk_info,
            "network": network_info,
        }

    def check_thresholds(self, data: Dict) -> List[Dict]:
        alerts = []

        # CPU alert
        if data["cpu"]["percent"] > self.thresholds["cpu"]:
            if self.alert_manager.should_alert("cpu"):
                alert = self.alert_manager.record_alert(
                    "cpu",
                    f"CPU usage at {data['cpu']['percent']:.1f}%",
                    "warning" if data["cpu"]["percent"] < 90 else "critical",
                    {
                        "usage": data["cpu"]["percent"],
                        "threshold": self.thresholds["cpu"],
                    },
                )
                alerts.append(alert)
                self.stats["alerts_triggered"] += 1

        # Memory alert
        if data["memory"]["percent"] > self.thresholds["memory"]:
            if self.alert_manager.should_alert("memory"):
                alert = self.alert_manager.record_alert(
                    "memory",
                    f"Memory usage at {data['memory']['percent']:.1f}%",
                    "warning" if data["memory"]["percent"] < 95 else "critical",
                    {
                        "usage": data["memory"]["percent"],
                        "threshold": self.thresholds["memory"],
                        "used": self._format_bytes(data["memory"]["used"]),
                        "total": self._format_bytes(data["memory"]["total"]),
                    },
                )
                alerts.append(alert)
                self.stats["alerts_triggered"] += 1

        # Disk alerts
        for mountpoint, disk_data in data["disk"]["partitions"].items():
            if disk_data["percent"] > self.thresholds["disk"]:
                alert_key = f"disk_{mountpoint}"
                if self.alert_manager.should_alert(alert_key):
                    alert = self.alert_manager.record_alert(
                        alert_key,
                        f"Disk {mountpoint} at {disk_data['percent']:.1f}%",
                        "warning" if disk_data["percent"] < 95 else "critical",
                        {
                            "mountpoint": mountpoint,
                            "usage": disk_data["percent"],
                            "threshold": self.thresholds["disk"],
                            "free": self._format_bytes(disk_data["free"]),
                            "total": self._format_bytes(disk_data["total"]),
                        },
                    )
                    alerts.append(alert)
                    self.stats["alerts_triggered"] += 1

        # Network alert
        total_network_speed = (
            data["network"]["speed_sent_mbps"] + data["network"]["speed_recv_mbps"]
        )
        if total_network_speed > self.thresholds["network"]:
            if self.alert_manager.should_alert("network"):
                alert = self.alert_manager.record_alert(
                    "network",
                    f"Network traffic at {total_network_speed:.1f} MB/s",
                    "info",
                    {
                        "speed_mbps": total_network_speed,
                        "threshold": self.thresholds["network"],
                        "sent": f"{data['network']['speed_sent_mbps']:.2f} MB/s",
                        "recv": f"{data['network']['speed_recv_mbps']:.2f} MB/s",
                    },
                )
                alerts.append(alert)
                self.stats["alerts_triggered"] += 1

        return alerts

    def print_status(self, data: Dict, alerts: List[Dict]):
        print("\n" + "=" * 80)
        print(f"System Monitor - {data['timestamp']}")
        print("=" * 80)

        # CPU
        cpu = data["cpu"]
        cpu_status = "🔴" if cpu["percent"] > self.thresholds["cpu"] else "🟢"
        print(
            f"\n{cpu_status} CPU Usage: {cpu['percent']:.1f}% (Threshold: {self.thresholds['cpu']:.1f}%)"
        )
        print(
            f"   Cores: {cpu['count']} | Load Average: {cpu['load_average']['1min']:.2f}, "
            f"{cpu['load_average']['5min']:.2f}, {cpu['load_average']['15min']:.2f}"
        )

        if cpu["frequency"]["current"]:
            print(
                f"   Frequency: {cpu['frequency']['current']:.0f} MHz "
                f"({cpu['frequency']['min']:.0f}-{cpu['frequency']['max']:.0f} MHz)"
            )

        # Memory
        mem = data["memory"]
        mem_status = "🔴" if mem["percent"] > self.thresholds["memory"] else "🟢"
        print(
            f"\n{mem_status} Memory Usage: {mem['percent']:.1f}% (Threshold: {self.thresholds['memory']:.1f}%)"
        )
        print(
            f"   Used: {self._format_bytes(mem['used'])} / {self._format_bytes(mem['total'])}"
        )
        print(f"   Available: {self._format_bytes(mem['available'])}")

        if mem["swap_total"] > 0:
            print(
                f"   Swap: {mem['swap_percent']:.1f}% ({self._format_bytes(mem['swap_used'])} / "
                f"{self._format_bytes(mem['swap_total'])})"
            )

        # Disk
        print("\n💾 Disk Usage:")
        for mountpoint, disk_data in sorted(data["disk"]["partitions"].items()):
            disk_status = (
                "🔴" if disk_data["percent"] > self.thresholds["disk"] else "🟢"
            )
            print(
                f"   {disk_status} {mountpoint}: {disk_data['percent']:.1f}% - "
                f"{self._format_bytes(disk_data['free'])} free of {self._format_bytes(disk_data['total'])}"
            )

        # Network
        net = data["network"]
        total_speed = net["speed_sent_mbps"] + net["speed_recv_mbps"]
        net_status = "🔴" if total_speed > self.thresholds["network"] else "🟢"
        print(
            f"\n{net_status} Network: ↑ {net['speed_sent_mbps']:.2f} MB/s | ↓ {net['speed_recv_mbps']:.2f} MB/s"
        )
        print(
            f"   Connections: {net['connections']['established']} established, "
            f"{net['connections']['listen']} listening"
        )
        print(
            f"   Total: ↑ {self._format_bytes(net['bytes_sent'])} | ↓ {self._format_bytes(net['bytes_recv'])}"
        )

        # Alerts
        if alerts:
            print("\n⚠️  ALERTS ({len(alerts)}):")
            for alert in alerts:
                severity_icon = {"info": "ℹ️", "warning": "⚠️", "critical": "🔥"}
                icon = severity_icon.get(alert["severity"], "⚠️")
                print(f"   {icon} [{alert['severity'].upper()}] {alert['message']}")

        # Statistics
        print("\n📊 Statistics:")
        print(
            f"   Checks: {self.stats['checks_performed']} | Alerts: {self.stats['alerts_triggered']}"
        )

        # Trending
        if len(self.history["cpu"]) > 1:
            cpu_trend = self.history["cpu"][-1] - self.history["cpu"][-2]
            mem_trend = self.history["memory"][-1] - self.history["memory"][-2]
            cpu_arrow = "↑" if cpu_trend > 0 else "↓" if cpu_trend < 0 else "→"
            mem_arrow = "↑" if mem_trend > 0 else "↓" if mem_trend < 0 else "→"
            print(
                f"   Trends: CPU {cpu_arrow} {abs(cpu_trend):.1f}% | Memory {mem_arrow} {abs(mem_trend):.1f}%"
            )

    def log_data(self, data: Dict, alerts: List[Dict]):
        if not self.log_file:
            return

        log_entry = {
            "timestamp": data["timestamp"],
            "data": data,
            "alerts": alerts,
            "stats": self.stats,
        }

        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except OSError as e:
            print(f"Error writing to log file: {e}")

    def export_report(self, output_file: str):
        report = {
            "generated": datetime.now().isoformat(),
            "monitoring_stats": self.stats,
            "thresholds": self.thresholds,
            "alert_summary": self.alert_manager.get_stats(),
            "current_status": self.check_resources(),
            "history": {
                "cpu": list(self.history["cpu"]),
                "memory": list(self.history["memory"]),
                "disk": list(self.history["disk"]),
                "network_sent": list(self.history["network_sent"]),
                "network_recv": list(self.history["network_recv"]),
            },
        }

        output_path = Path(output_file)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"Report exported to: {output_path}")

    def run(self, duration: Optional[int] = None, show_processes: bool = False):
        print(f"Starting system monitor (check interval: {self.check_interval}s)")
        print(
            f"Thresholds: CPU={self.thresholds['cpu']}%, Memory={self.thresholds['memory']}%, "
            f"Disk={self.thresholds['disk']}%, Network={self.thresholds['network']} MB/s"
        )
        print("Press Ctrl+C to stop")

        start_time = time.time()

        try:
            while self.running:
                data = self.check_resources()
                alerts = self.check_thresholds(data)

                self.print_status(data, alerts)

                if show_processes:
                    proc_info = self._get_process_info()
                    print("\n🔝 Top Processes (CPU):")
                    for proc in proc_info["top_cpu"]:
                        print(
                            f"   {proc['name'][:30]:30} | CPU: {proc['cpu_percent']:5.1f}% | "
                            f"MEM: {proc['memory_percent']:5.1f}%"
                        )

                self.log_data(data, alerts)

                if duration and (time.time() - start_time) >= duration:
                    break

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")

        # Final statistics
        runtime = time.time() - start_time
        print(f"\n{'=' * 80}")
        print("Monitoring Summary")
        print(f"{'=' * 80}")
        print(f"Runtime: {runtime:.0f}s")
        print(f"Total checks: {self.stats['checks_performed']}")
        print(f"Total alerts: {self.stats['alerts_triggered']}")

        alert_stats = self.alert_manager.get_stats()
        if alert_stats["alerts_by_type"]:
            print("\nAlerts by type:")
            for alert_type, count in alert_stats["alerts_by_type"].items():
                print(f"  {alert_type}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="System Resource Monitor with Alerts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic monitoring with default thresholds
  python system_monitor.py

  # Custom thresholds
  python system_monitor.py --cpu-threshold 70 --memory-threshold 80

  # Monitor for specific duration
  python system_monitor.py --duration 300

  # Save logs and export report
  python system_monitor.py --log monitor.log --export-report report.json

  # Show top processes
  python system_monitor.py --show-processes

  # Quick status check (single check)
  python system_monitor.py --once
        """,
    )

    parser.add_argument(
        "--cpu-threshold",
        type=float,
        default=80.0,
        help="CPU usage alert threshold (default: 80%%)",
    )
    parser.add_argument(
        "--memory-threshold",
        type=float,
        default=85.0,
        help="Memory usage alert threshold (default: 85%%)",
    )
    parser.add_argument(
        "--disk-threshold",
        type=float,
        default=90.0,
        help="Disk usage alert threshold (default: 90%%)",
    )
    parser.add_argument(
        "--network-threshold",
        type=float,
        default=100.0,
        help="Network speed alert threshold in MB/s (default: 100)",
    )

    parser.add_argument(
        "--interval", type=int, default=5, help="Check interval in seconds (default: 5)"
    )
    parser.add_argument(
        "--duration",
        type=int,
        help="Monitoring duration in seconds (default: unlimited)",
    )
    parser.add_argument(
        "--cooldown",
        type=int,
        default=300,
        help="Alert cooldown period in seconds (default: 300)",
    )

    parser.add_argument(
        "--log", type=str, help="Log file path for continuous monitoring data"
    )
    parser.add_argument(
        "--export-report", type=str, help="Export detailed report to JSON file"
    )

    parser.add_argument(
        "--show-processes",
        action="store_true",
        help="Show top processes by CPU and memory",
    )
    parser.add_argument(
        "--once", action="store_true", help="Perform single check and exit"
    )

    args = parser.parse_args()

    if not HAS_PSUTIL:
        print("Error: psutil library is required. Install with: pip install psutil")
        sys.exit(1)

    try:
        monitor = ResourceMonitor(
            cpu_threshold=args.cpu_threshold,
            memory_threshold=args.memory_threshold,
            disk_threshold=args.disk_threshold,
            network_threshold=args.network_threshold,
            check_interval=args.interval,
            alert_cooldown=args.cooldown,
            log_file=args.log,
        )

        if args.once:
            # Single check mode
            data = monitor.check_resources()
            alerts = monitor.check_thresholds(data)
            monitor.print_status(data, alerts)

            if args.show_processes:
                proc_info = monitor._get_process_info()
                print("\n🔝 Top Processes (CPU):")
                for proc in proc_info["top_cpu"]:
                    print(
                        f"   {proc['name'][:30]:30} | CPU: {proc['cpu_percent']:5.1f}% | "
                        f"MEM: {proc['memory_percent']:5.1f}%"
                    )
        else:
            # Continuous monitoring mode
            monitor.run(duration=args.duration, show_processes=args.show_processes)

        # Export report if requested
        if args.export_report:
            monitor.export_report(args.export_report)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
