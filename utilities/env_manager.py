#!/usr/bin/env python3

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class EnvVariable:
    key: str
    value: str
    required: bool = False
    description: Optional[str] = None
    default: Optional[str] = None
    pattern: Optional[str] = None


class EnvManager:
    def __init__(self):
        self.variables: Dict[str, EnvVariable] = {}
        self.stats = {
            "total_vars": 0,
            "required_vars": 0,
            "missing_vars": 0,
            "invalid_vars": 0,
        }

    def load_env(self, filepath: Path) -> Dict[str, str]:
        env_vars = {}

        with open(filepath) as f:
            for _line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse KEY=VALUE
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    env_vars[key] = value
                    self.variables[key] = EnvVariable(key=key, value=value)

        self.stats["total_vars"] = len(env_vars)
        return env_vars

    def save_env(
        self, filepath: Path, variables: Dict[str, str], comments: bool = True
    ):
        with open(filepath, "w") as f:
            if comments:
                f.write("# Environment Variables\n")
                f.write(f"# Generated: {Path(__file__).name}\n\n")

            for key, value in sorted(variables.items()):
                # Add description if available
                if (
                    comments
                    and key in self.variables
                    and self.variables[key].description
                ):
                    f.write(f"# {self.variables[key].description}\n")

                # Quote value if it contains spaces or special chars
                if " " in value or any(c in value for c in "!@#$%^&*()"):
                    value = f'"{value}"'

                f.write(f"{key}={value}\n")

    def load_template(self, filepath: Path) -> Dict[str, EnvVariable]:
        template = {}

        with open(filepath) as f:
            data = json.load(f)

        for key, spec in data.items():
            if isinstance(spec, dict):
                template[key] = EnvVariable(
                    key=key,
                    value=spec.get("default", ""),
                    required=spec.get("required", False),
                    description=spec.get("description"),
                    default=spec.get("default"),
                    pattern=spec.get("pattern"),
                )
                if spec.get("required"):
                    self.stats["required_vars"] += 1
            else:
                template[key] = EnvVariable(key=key, value=str(spec))

        return template

    def generate_template(self, env_file: Path, output_file: Path):
        env_vars = self.load_env(env_file)

        template = {}
        for key, value in env_vars.items():
            template[key] = {
                "description": f"Description for {key}",
                "required": False,
                "default": value,
                "pattern": None,
            }

        with open(output_file, "w") as f:
            json.dump(template, f, indent=2)

        print(f"✓ Template generated: {output_file}")

    def generate_example(self, template_file: Path, output_file: Path):
        template = self.load_template(template_file)

        with open(output_file, "w") as f:
            f.write("# Environment Variables Example\n")
            f.write("# Copy this file to .env and fill in your values\n\n")

            for key, var in sorted(template.items()):
                if var.description:
                    f.write(f"# {var.description}\n")
                if var.required:
                    f.write("# REQUIRED\n")
                if var.pattern:
                    f.write(f"# Pattern: {var.pattern}\n")

                value = var.default or ""
                if var.required and not value:
                    value = f"<YOUR_{key}_HERE>"

                f.write(f"{key}={value}\n\n")

        print(f"✓ Example generated: {output_file}")

    def validate(self, env_file: Path, template_file: Path) -> List[str]:
        env_vars = self.load_env(env_file)
        template = self.load_template(template_file)

        errors = []

        # Check required variables
        for key, var in template.items():
            if var.required and key not in env_vars:
                errors.append(f"Missing required variable: {key}")
                self.stats["missing_vars"] += 1

            # Validate pattern
            if key in env_vars and var.pattern:
                if not re.match(var.pattern, env_vars[key]):
                    errors.append(
                        f"Invalid format for {key}: does not match pattern {var.pattern}"
                    )
                    self.stats["invalid_vars"] += 1

        # Check for unknown variables
        unknown = set(env_vars.keys()) - set(template.keys())
        for key in unknown:
            errors.append(f"Unknown variable: {key}")

        return errors

    def merge(self, base_file: Path, override_file: Path, output_file: Path):
        base = self.load_env(base_file)
        override = self.load_env(override_file)

        merged = {**base, **override}
        self.save_env(output_file, merged)

        print(f"✓ Merged {len(base)} + {len(override)} = {len(merged)} variables")

    def diff(self, file1: Path, file2: Path) -> Dict[str, any]:
        vars1 = self.load_env(file1)
        vars2 = self.load_env(file2)

        diff = {"added": {}, "removed": {}, "changed": {}}

        for key in vars2:
            if key not in vars1:
                diff["added"][key] = vars2[key]
            elif vars1[key] != vars2[key]:
                diff["changed"][key] = {"old": vars1[key], "new": vars2[key]}

        for key in vars1:
            if key not in vars2:
                diff["removed"][key] = vars1[key]

        return diff

    def print_diff(self, diff: Dict):
        print("\n" + "=" * 60)
        print("ENVIRONMENT DIFFERENCES")
        print("=" * 60)

        if diff["added"]:
            print("\n➕ Added Variables:")
            for key, value in diff["added"].items():
                print(f"  {key}={value}")

        if diff["removed"]:
            print("\n➖ Removed Variables:")
            for key, value in diff["removed"].items():
                print(f"  {key}={value}")

        if diff["changed"]:
            print("\n🔄 Changed Variables:")
            for key, values in diff["changed"].items():
                print(f"  {key}:")
                print(f"    Old: {values['old']}")
                print(f"    New: {values['new']}")

        if not any(diff.values()):
            print("\n✓ No differences")

    def print_validation_report(self, errors: List[str]):
        print("\n" + "=" * 60)
        print("VALIDATION REPORT")
        print("=" * 60)
        print(f"Total variables:   {self.stats['total_vars']}")
        print(f"Required:          {self.stats['required_vars']}")
        print(f"Missing:           {self.stats['missing_vars']}")
        print(f"Invalid format:    {self.stats['invalid_vars']}")

        if errors:
            print(f"\n❌ Found {len(errors)} issue(s):")
            for error in errors:
                print(f"  • {error}")
        else:
            print("\n✓ All validations passed")


def main():
    parser = argparse.ArgumentParser(
        description="Manage environment variables and .env files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate .env against template
  python env_manager.py --validate .env --template .env.template.json

  # Generate template from .env
  python env_manager.py --generate-template .env -o .env.template.json

  # Generate .env.example
  python env_manager.py --generate-example .env.template.json -o .env.example

  # Merge environments
  python env_manager.py --merge .env.base .env.local -o .env

  # Show differences
  python env_manager.py --diff .env.dev .env.prod

Template format (JSON):
{
  "DATABASE_URL": {
    "description": "Database connection string",
    "required": true,
    "pattern": "^postgresql://.*"
  },
  "API_KEY": {
    "description": "API authentication key",
    "required": true
  },
  "DEBUG": {
    "description": "Enable debug mode",
    "required": false,
    "default": "false"
  }
}
        """,
    )

    parser.add_argument("--validate", type=Path, help="Validate .env file")
    parser.add_argument("--template", type=Path, help="Template file (JSON)")

    parser.add_argument(
        "--generate-template", type=Path, help="Generate template from .env file"
    )
    parser.add_argument(
        "--generate-example", type=Path, help="Generate .env.example from template"
    )

    parser.add_argument(
        "--merge",
        nargs=2,
        type=Path,
        metavar=("BASE", "OVERRIDE"),
        help="Merge two .env files",
    )
    parser.add_argument(
        "--diff",
        nargs=2,
        type=Path,
        metavar=("FILE1", "FILE2"),
        help="Show differences between .env files",
    )

    parser.add_argument("-o", "--output", type=Path, help="Output file")

    args = parser.parse_args()

    try:
        manager = EnvManager()

        # Validate mode
        if args.validate:
            if not args.template:
                parser.error("--validate requires --template")

            errors = manager.validate(args.validate, args.template)
            manager.print_validation_report(errors)
            sys.exit(0 if not errors else 1)

        # Generate template
        if args.generate_template:
            if not args.output:
                parser.error("--generate-template requires --output")
            manager.generate_template(args.generate_template, args.output)
            sys.exit(0)

        # Generate example
        if args.generate_example:
            if not args.output:
                parser.error("--generate-example requires --output")
            manager.generate_example(args.generate_example, args.output)
            sys.exit(0)

        # Merge
        if args.merge:
            if not args.output:
                parser.error("--merge requires --output")
            manager.merge(args.merge[0], args.merge[1], args.output)
            sys.exit(0)

        # Diff
        if args.diff:
            diff = manager.diff(args.diff[0], args.diff[1])
            manager.print_diff(diff)
            sys.exit(0)

        parser.print_help()

    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
