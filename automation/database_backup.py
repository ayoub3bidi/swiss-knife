#!/usr/bin/env python3

import argparse
import gzip
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class DatabaseBackup:
    SUPPORTED_TYPES = ["mysql", "postgresql", "mongodb", "sqlite"]

    def __init__(
        self,
        db_type: str,
        output_dir: Path,
        compress: bool = True,
        keep_days: int = 7,
        keep_weekly: int = 4,
        keep_monthly: int = 3,
    ):
        """
        Args:
            db_type: Database type (mysql, postgresql, mongodb, sqlite)
            output_dir: Directory to store backups
            compress: Compress backups with gzip
            keep_days: Keep daily backups for N days
            keep_weekly: Keep weekly backups for N weeks
            keep_monthly: Keep monthly backups for N months
        """
        if db_type.lower() not in self.SUPPORTED_TYPES:
            raise ValueError(f"Unsupported database type: {db_type}")

        self.db_type = db_type.lower()
        self.output_dir = Path(output_dir)
        self.compress = compress
        self.keep_days = keep_days
        self.keep_weekly = keep_weekly
        self.keep_monthly = keep_monthly

        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.stats = {
            "backups_created": 0,
            "backups_deleted": 0,
            "total_size": 0,
            "compression_ratio": 0,
        }

    def _format_size(self, bytes_val: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_val < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} PB"

    def _calculate_checksum(self, filepath: Path) -> str:
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def _compress_file(self, filepath: Path) -> Path:
        compressed_path = filepath.with_suffix(filepath.suffix + ".gz")

        print(f"Compressing {filepath.name}...")
        with open(filepath, "rb") as f_in:
            with gzip.open(compressed_path, "wb", compresslevel=6) as f_out:
                shutil.copyfileobj(f_in, f_out)

        original_size = filepath.stat().st_size
        compressed_size = compressed_path.stat().st_size
        ratio = (compressed_size / original_size * 100) if original_size > 0 else 0

        print(
            f"Compressed: {self._format_size(original_size)} → {self._format_size(compressed_size)} ({ratio:.1f}%)"
        )

        filepath.unlink()

        return compressed_path

    def _backup_mysql(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        output_file: Path,
    ) -> bool:
        """Backup MySQL database."""
        cmd = [
            "mysqldump",
            f"--host={host}",
            f"--port={port}",
            f"--user={user}",
            f"--password={password}",
            "--single-transaction",
            "--quick",
            "--lock-tables=false",
            database,
        ]

        try:
            with open(output_file, "w") as f:
                result = subprocess.run(
                    cmd, stdout=f, stderr=subprocess.PIPE, text=True, timeout=3600
                )

            if result.returncode != 0:
                print(f"MySQL backup error: {result.stderr}")
                return False

            return True

        except subprocess.TimeoutExpired:
            print("MySQL backup timed out")
            return False
        except FileNotFoundError:
            print("Error: mysqldump not found. Install MySQL client tools.")
            return False
        except Exception as e:
            print(f"MySQL backup error: {e}")
            return False

    def _backup_postgresql(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        output_file: Path,
    ) -> bool:
        env = {"PGPASSWORD": password}

        cmd = [
            "pg_dump",
            f"--host={host}",
            f"--port={port}",
            f"--username={user}",
            "--format=custom",
            "--verbose",
            database,
        ]

        try:
            with open(output_file, "wb") as f:
                result = subprocess.run(
                    cmd,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    env={**subprocess.os.environ, **env},
                    timeout=3600,
                )

            if result.returncode != 0:
                print(f"PostgreSQL backup error: {result.stderr.decode()}")
                return False

            return True

        except subprocess.TimeoutExpired:
            print("PostgreSQL backup timed out")
            return False
        except FileNotFoundError:
            print("Error: pg_dump not found. Install PostgreSQL client tools.")
            return False
        except Exception as e:
            print(f"PostgreSQL backup error: {e}")
            return False

    def _backup_mongodb(
        self,
        host: str,
        port: int,
        user: Optional[str],
        password: Optional[str],
        database: str,
        output_file: Path,
    ) -> bool:
        # MongoDB dumps to directory, we'll use archive format
        cmd = [
            "mongodump",
            f"--host={host}",
            f"--port={port}",
            f"--db={database}",
            f"--archive={output_file}",
            "--gzip",
        ]

        if user:
            cmd.extend([f"--username={user}", f"--password={password}"])

        try:
            result = subprocess.run(
                cmd, stderr=subprocess.PIPE, text=True, timeout=3600
            )

            if result.returncode != 0:
                print(f"MongoDB backup error: {result.stderr}")
                return False

            return True

        except subprocess.TimeoutExpired:
            print("MongoDB backup timed out")
            return False
        except FileNotFoundError:
            print("Error: mongodump not found. Install MongoDB database tools.")
            return False
        except Exception as e:
            print(f"MongoDB backup error: {e}")
            return False

    def _backup_sqlite(self, database_path: str, output_file: Path) -> bool:
        try:
            db_path = Path(database_path)
            if not db_path.exists():
                print(f"Error: SQLite database not found: {database_path}")
                return False

            # Simple file copy for SQLite
            shutil.copy2(db_path, output_file)
            return True

        except Exception as e:
            print(f"SQLite backup error: {e}")
            return False

    def backup(
        self,
        host: str = "localhost",
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: str = None,
        database_path: Optional[str] = None,
    ) -> Optional[Path]:
        if port is None:
            ports = {"mysql": 3306, "postgresql": 5432, "mongodb": 27017}
            port = ports.get(self.db_type, 0)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        db_name = database or Path(database_path).stem if database_path else "backup"

        if self.db_type == "postgresql":
            extension = ".dump"
        elif self.db_type == "mongodb":
            extension = ".archive"
        else:
            extension = ".sql"

        filename = f"{self.db_type}_{db_name}_{timestamp}{extension}"
        output_file = self.output_dir / filename

        print(f"\n{'=' * 60}")
        print(f"Creating {self.db_type.upper()} backup")
        print(f"{'=' * 60}")
        print(f"Database: {database or database_path}")
        print(f"Output:   {output_file}")

        success = False

        if self.db_type == "mysql":
            success = self._backup_mysql(
                host, port, user, password, database, output_file
            )
        elif self.db_type == "postgresql":
            success = self._backup_postgresql(
                host, port, user, password, database, output_file
            )
        elif self.db_type == "mongodb":
            success = self._backup_mongodb(
                host, port, user, password, database, output_file
            )
        elif self.db_type == "sqlite":
            success = self._backup_sqlite(database_path, output_file)

        if not success:
            if output_file.exists():
                output_file.unlink()
            return None

        file_size = output_file.stat().st_size
        print(f"Backup size: {self._format_size(file_size)}")

        if self.compress and self.db_type != "mongodb":
            output_file = self._compress_file(output_file)
            file_size = output_file.stat().st_size

        checksum = self._calculate_checksum(output_file)

        metadata = {
            "timestamp": datetime.now().isoformat(),
            "database_type": self.db_type,
            "database_name": database or db_name,
            "filename": output_file.name,
            "size_bytes": file_size,
            "compressed": self.compress or self.db_type == "mongodb",
            "checksum_sha256": checksum,
        }

        metadata_file = output_file.with_suffix(output_file.suffix + ".json")
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

        self.stats["backups_created"] += 1
        self.stats["total_size"] += file_size

        print(f"✓ Backup completed: {output_file.name}")
        print(f"Checksum: {checksum[:16]}...")

        return output_file

    def _get_backup_date(self, filepath: Path) -> Optional[datetime]:
        try:
            metadata_file = filepath.with_suffix(filepath.suffix + ".json")
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                return datetime.fromisoformat(metadata["timestamp"])

            # Fallback to filename parsing
            # Format: dbtype_dbname_YYYYMMDD_HHMMSS.ext
            parts = filepath.stem.split("_")
            if len(parts) >= 3:
                date_str = parts[-2] + parts[-1]  # YYYYMMDD + HHMMSS
                return datetime.strptime(date_str, "%Y%m%d%H%M%S")
        except Exception:
            pass

        return None

    def rotate_backups(self) -> None:
        print(f"\n{'=' * 60}")
        print("Rotating backups")
        print(f"{'=' * 60}")

        now = datetime.now()
        backups = []

        for filepath in self.output_dir.glob(f"{self.db_type}_*"):
            if filepath.suffix in [".sql", ".dump", ".archive", ".gz"] or (
                filepath.suffix == ".db" and self.db_type == "sqlite"
            ):
                backup_date = self._get_backup_date(filepath)
                if backup_date:
                    backups.append((filepath, backup_date))

        backups.sort(key=lambda x: x[1], reverse=True)

        to_delete = []
        weekly_kept = []
        monthly_kept = []

        for filepath, backup_date in backups:
            age_days = (now - backup_date).days

            if age_days < self.keep_days:
                continue

            # Keep weekly backups (first backup of each week)
            week_key = backup_date.strftime("%Y-W%W")
            if age_days < self.keep_days + (self.keep_weekly * 7):
                if week_key not in weekly_kept:
                    weekly_kept.append(week_key)
                    continue

            # Keep monthly backups (first backup of each month)
            month_key = backup_date.strftime("%Y-%m")
            if age_days < self.keep_days + (self.keep_weekly * 7) + (
                self.keep_monthly * 30
            ):
                if month_key not in monthly_kept:
                    monthly_kept.append(month_key)
                    continue

            # Mark for deletion
            to_delete.append(filepath)

        if not to_delete:
            print("No backups to delete")
            return

        print(f"Deleting {len(to_delete)} old backup(s):")
        for filepath in to_delete:
            print(f"  - {filepath.name}")

            # Delete backup file
            filepath.unlink()

            # Delete metadata if exists
            metadata_file = filepath.with_suffix(filepath.suffix + ".json")
            if metadata_file.exists():
                metadata_file.unlink()

            self.stats["backups_deleted"] += 1

        print("✓ Rotation completed")

    def list_backups(self) -> List[Dict]:
        backups = []

        for filepath in self.output_dir.glob(f"{self.db_type}_*"):
            if filepath.suffix in [".sql", ".dump", ".archive", ".gz"] or (
                filepath.suffix == ".db" and self.db_type == "sqlite"
            ):
                backup_date = self._get_backup_date(filepath)
                size = filepath.stat().st_size

                backup_info = {
                    "filename": filepath.name,
                    "path": str(filepath),
                    "date": backup_date.isoformat() if backup_date else None,
                    "age_days": (datetime.now() - backup_date).days
                    if backup_date
                    else None,
                    "size": size,
                    "size_formatted": self._format_size(size),
                }

                backups.append(backup_info)

        backups.sort(key=lambda x: x["date"] or "", reverse=True)
        return backups

    def print_backups(self) -> None:
        backups = self.list_backups()

        if not backups:
            print("No backups found")
            return

        print(f"\n{'=' * 60}")
        print(f"Existing backups: {len(backups)}")
        print(f"{'=' * 60}")

        total_size = sum(b["size"] for b in backups)

        for backup in backups:
            age = (
                f"{backup['age_days']}d ago"
                if backup["age_days"] is not None
                else "unknown"
            )
            print(
                f"{backup['filename']:50s} {backup['size_formatted']:>10s} {age:>12s}"
            )

        print(f"\nTotal size: {self._format_size(total_size)}")

    def print_summary(self):
        print(f"\n{'=' * 60}")
        print("BACKUP SUMMARY")
        print(f"{'=' * 60}")
        print(f"Backups created:  {self.stats['backups_created']}")
        print(f"Backups deleted:  {self.stats['backups_deleted']}")
        print(f"Total size:       {self._format_size(self.stats['total_size'])}")


def main():
    parser = argparse.ArgumentParser(
        description="Automated database backup with compression and rotation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # MySQL backup
  python database_backup.py mysql -d mydb -u root -p password -o backups/

  # PostgreSQL backup
  python database_backup.py postgresql -d mydb -u postgres -p pass -o backups/

  # MongoDB backup
  python database_backup.py mongodb -d mydb -u admin -p pass -o backups/

  # SQLite backup
  python database_backup.py sqlite --db-path /path/to/database.db -o backups/

  # With custom retention
  python database_backup.py mysql -d mydb -u root -p pass -o backups/ --keep-days 14 --keep-weekly 8

  # List existing backups
  python database_backup.py mysql -o backups/ --list

  # Rotate old backups
  python database_backup.py mysql -o backups/ --rotate-only
        """,
    )

    parser.add_argument(
        "db_type",
        choices=["mysql", "postgresql", "mongodb", "sqlite"],
        help="Database type",
    )

    parser.add_argument(
        "-o", "--output", type=Path, required=True, help="Output directory for backups"
    )

    parser.add_argument(
        "-H", "--host", default="localhost", help="Database host (default: localhost)"
    )
    parser.add_argument(
        "-P", "--port", type=int, help="Database port (default: depends on db type)"
    )
    parser.add_argument("-u", "--user", help="Database user")
    parser.add_argument("-p", "--password", help="Database password")
    parser.add_argument("-d", "--database", help="Database name")
    parser.add_argument("--db-path", help="SQLite database file path")

    parser.add_argument(
        "--no-compress",
        dest="compress",
        action="store_false",
        help="Don't compress backups",
    )
    parser.add_argument(
        "--keep-days",
        type=int,
        default=7,
        help="Keep daily backups for N days (default: 7)",
    )
    parser.add_argument(
        "--keep-weekly",
        type=int,
        default=4,
        help="Keep weekly backups for N weeks (default: 4)",
    )
    parser.add_argument(
        "--keep-monthly",
        type=int,
        default=3,
        help="Keep monthly backups for N months (default: 3)",
    )

    parser.add_argument("--list", action="store_true", help="List existing backups")
    parser.add_argument(
        "--rotate-only",
        action="store_true",
        help="Only rotate old backups, don't create new one",
    )

    args = parser.parse_args()

    if not args.rotate_only and not args.list:
        if args.db_type == "sqlite":
            if not args.db_path:
                parser.error("SQLite requires --db-path")
        else:
            if not args.database:
                parser.error(f"{args.db_type} requires --database")
            if not args.user:
                parser.error(f"{args.db_type} requires --user")
            if not args.password:
                parser.error(f"{args.db_type} requires --password")

    try:
        backup = DatabaseBackup(
            db_type=args.db_type,
            output_dir=args.output,
            compress=args.compress,
            keep_days=args.keep_days,
            keep_weekly=args.keep_weekly,
            keep_monthly=args.keep_monthly,
        )

        if args.list:
            backup.print_backups()
            return

        if not args.rotate_only:
            result = backup.backup(
                host=args.host,
                port=args.port,
                user=args.user,
                password=args.password,
                database=args.database,
                database_path=args.db_path,
            )

            if not result:
                print("\n✗ Backup failed")
                sys.exit(1)

        backup.rotate_backups()

        backup.print_summary()

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
