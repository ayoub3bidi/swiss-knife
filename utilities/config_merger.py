#!/usr/bin/env python3

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import toml

    HAS_TOML = True
except ImportError:
    HAS_TOML = False

import configparser


class ConfigMerger:
    SUPPORTED_FORMATS = ["json", "yaml", "yml", "toml", "ini", "env"]

    def __init__(self, strategy: str = "override"):
        """
        Args:
            strategy: Merge strategy ('override', 'merge', 'append')
        """
        self.strategy = strategy
        self.stats = {"files_merged": 0, "conflicts": 0, "keys_total": 0}

    def _detect_format(self, filepath: Path) -> str:
        ext = filepath.suffix.lower().lstrip(".")
        if ext in self.SUPPORTED_FORMATS:
            return ext
        raise ValueError(f"Unsupported format: {ext}")

    def load_config(self, filepath: Path) -> Dict[str, Any]:
        format_type = self._detect_format(filepath)

        if format_type == "json":
            return self._load_json(filepath)
        elif format_type in ["yaml", "yml"]:
            return self._load_yaml(filepath)
        elif format_type == "toml":
            return self._load_toml(filepath)
        elif format_type == "ini":
            return self._load_ini(filepath)
        elif format_type == "env":
            return self._load_env(filepath)

        raise ValueError(f"Unsupported format: {format_type}")

    def _load_json(self, filepath: Path) -> Dict:
        with open(filepath) as f:
            return json.load(f)

    def _load_yaml(self, filepath: Path) -> Dict:
        if not HAS_YAML:
            raise ImportError("PyYAML not installed. Run: pip install pyyaml")
        with open(filepath) as f:
            return yaml.safe_load(f) or {}

    def _load_toml(self, filepath: Path) -> Dict:
        if not HAS_TOML:
            raise ImportError("toml not installed. Run: pip install toml")
        with open(filepath) as f:
            return toml.load(f)

    def _load_ini(self, filepath: Path) -> Dict:
        config = configparser.ConfigParser()
        config.read(filepath)
        return {section: dict(config[section]) for section in config.sections()}

    def _load_env(self, filepath: Path) -> Dict:
        env_vars = {}
        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip().strip("\"'")
        return env_vars

    def save_config(
        self, data: Dict, filepath: Path, format_type: Optional[str] = None
    ):
        if format_type is None:
            format_type = self._detect_format(filepath)

        if format_type == "json":
            self._save_json(data, filepath)
        elif format_type in ["yaml", "yml"]:
            self._save_yaml(data, filepath)
        elif format_type == "toml":
            self._save_toml(data, filepath)
        elif format_type == "ini":
            self._save_ini(data, filepath)
        elif format_type == "env":
            self._save_env(data, filepath)

    def _save_json(self, data: Dict, filepath: Path):
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def _save_yaml(self, data: Dict, filepath: Path):
        if not HAS_YAML:
            raise ImportError("PyYAML not installed")
        with open(filepath, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def _save_toml(self, data: Dict, filepath: Path):
        if not HAS_TOML:
            raise ImportError("toml not installed")
        with open(filepath, "w") as f:
            toml.dump(data, f)

    def _save_ini(self, data: Dict, filepath: Path):
        config = configparser.ConfigParser()
        for section, values in data.items():
            config[section] = values
        with open(filepath, "w") as f:
            config.write(f)

    def _save_env(self, data: Dict, filepath: Path):
        with open(filepath, "w") as f:
            for key, value in data.items():
                f.write(f"{key}={value}\n")

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        result = deepcopy(base)

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            elif (
                key in result
                and isinstance(result[key], list)
                and isinstance(value, list)
            ):
                if self.strategy == "append":
                    result[key].extend(value)
                else:
                    result[key] = value
            else:
                if key in result and result[key] != value:
                    self.stats["conflicts"] += 1
                result[key] = value

        return result

    def merge_configs(self, base_config: Dict, *override_configs: Dict) -> Dict:
        result = deepcopy(base_config)

        for override in override_configs:
            if self.strategy == "override":
                result.update(override)
            elif self.strategy == "merge":
                result = self._deep_merge(result, override)
            elif self.strategy == "append":
                result = self._deep_merge(result, override)

        return result

    def merge_files(
        self, base_file: Path, *override_files: Path, output_file: Optional[Path] = None
    ) -> Dict:
        print(f"Merging {len(override_files) + 1} configuration file(s)...")

        # Load base
        print(f"  Base: {base_file}")
        base_config = self.load_config(base_file)
        self.stats["files_merged"] += 1

        # Load overrides
        override_configs = []
        for filepath in override_files:
            print(f"  Override: {filepath}")
            override_configs.append(self.load_config(filepath))
            self.stats["files_merged"] += 1

        # Merge
        result = self.merge_configs(base_config, *override_configs)

        # Count keys
        self.stats["keys_total"] = self._count_keys(result)

        # Save if output specified
        if output_file:
            self.save_config(result, output_file)
            print(f"\n✓ Merged configuration saved to: {output_file}")

        return result

    def _count_keys(self, data: Any, count: int = 0) -> int:
        if isinstance(data, dict):
            count += len(data)
            for value in data.values():
                count = self._count_keys(value, count)
        elif isinstance(data, list):
            for item in data:
                count = self._count_keys(item, count)
        return count

    def diff_configs(self, config1: Path, config2: Path) -> Dict:
        data1 = self.load_config(config1)
        data2 = self.load_config(config2)

        diff = {"added": {}, "removed": {}, "changed": {}}

        # Find added and changed
        for key in data2:
            if key not in data1:
                diff["added"][key] = data2[key]
            elif data1[key] != data2[key]:
                diff["changed"][key] = {"old": data1[key], "new": data2[key]}

        # Find removed
        for key in data1:
            if key not in data2:
                diff["removed"][key] = data1[key]

        return diff

    def print_diff(self, diff: Dict):
        print("\n" + "=" * 60)
        print("CONFIGURATION DIFFERENCES")
        print("=" * 60)

        if diff["added"]:
            print("\n➕ Added Keys:")
            for key, value in diff["added"].items():
                print(f"  {key}: {value}")

        if diff["removed"]:
            print("\n➖ Removed Keys:")
            for key, value in diff["removed"].items():
                print(f"  {key}: {value}")

        if diff["changed"]:
            print("\n🔄 Changed Keys:")
            for key, values in diff["changed"].items():
                print(f"  {key}:")
                print(f"    Old: {values['old']}")
                print(f"    New: {values['new']}")

        if not any(diff.values()):
            print("\n✓ No differences found")

    def print_stats(self):
        print("\n" + "=" * 60)
        print("MERGE STATISTICS")
        print("=" * 60)
        print(f"Files merged:  {self.stats['files_merged']}")
        print(f"Total keys:    {self.stats['keys_total']}")
        print(f"Conflicts:     {self.stats['conflicts']}")


def main():
    parser = argparse.ArgumentParser(
        description="Merge and manage configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Merge configs (base + overrides)
  python config_merger.py base.json dev.json -o config.json

  # Merge multiple environments
  python config_merger.py base.json common.json prod.json -o prod-final.json

  # Deep merge strategy
  python config_merger.py base.yaml override.yaml -o merged.yaml --strategy merge

  # Show differences
  python config_merger.py config1.json config2.json --diff

  # Convert format
  python config_merger.py config.json -o config.yaml

  # Cross-format merge
  python config_merger.py base.yaml override.toml -o final.json

Supported formats: json, yaml, yml, toml, ini, env
Strategies: override (default), merge (deep), append (lists)
        """,
    )

    parser.add_argument(
        "files", nargs="+", type=Path, help="Configuration files (first is base)"
    )

    parser.add_argument("-o", "--output", type=Path, help="Output file")
    parser.add_argument(
        "--strategy",
        choices=["override", "merge", "append"],
        default="override",
        help="Merge strategy (default: override)",
    )

    parser.add_argument(
        "--diff",
        action="store_true",
        help="Show differences (requires exactly 2 files)",
    )
    parser.add_argument(
        "--print", action="store_true", help="Print merged result to stdout"
    )

    args = parser.parse_args()

    # Validate files
    for filepath in args.files:
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)

    try:
        merger = ConfigMerger(strategy=args.strategy)

        # Diff mode
        if args.diff:
            if len(args.files) != 2:
                print("Error: --diff requires exactly 2 files")
                sys.exit(1)

            diff = merger.diff_configs(args.files[0], args.files[1])
            merger.print_diff(diff)
            sys.exit(0)

        # Merge mode
        base = args.files[0]
        overrides = args.files[1:] if len(args.files) > 1 else []

        result = merger.merge_files(base, *overrides, output_file=args.output)

        # Print result if requested
        if args.print:
            print("\n" + "=" * 60)
            print("MERGED CONFIGURATION")
            print("=" * 60)
            print(json.dumps(result, indent=2))

        merger.print_stats()

    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
