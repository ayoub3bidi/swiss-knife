# AGENTS.md

Repository guidance for agents working in this workspace.

## Scope

- The installable package is `swiss_knife/` (PyPI name: `swiss-knife-py`, import: `swiss_knife`).
- Current release: **0.1.3** on PyPI. Base install has **zero runtime dependencies**.
- Standalone script trees live under `scripts/` and are **not** installed by `pip install swiss-knife-py`:
  `scripts/automation/`, `scripts/convert/`, `scripts/file_management/`, `scripts/network_web/`, `scripts/system_utilities/`, `scripts/text_processing/`, `scripts/utilities/`, `scripts/development_tools/`.
- Do not treat standalone scripts as package APIs. Many mirror or predate the packaged modules under `swiss_knife/`.

## Package Layout

```
swiss_knife/
├── __init__.py              # __version__, SafetyError, ValidationError + utilities re-exports
├── core.py                  # validate_path, safe_filename, confirm_destructive_action, ...
├── utilities/
│   └── common.py            # parse_bool, get_env_*, is_empty, is_not_empty, convert_keys_to_camel_case, ...
├── automation/
│   └── password_generator.py
├── file_management/
│   ├── duplicate_finder.py
│   └── bulk_renamer.py
├── text_processing/
│   └── csv_converter.py
└── cli/
    ├── _common.py           # Shared CLI helpers (--version)
    ├── main.py              # sk (umbrella: version + tool listing)
    ├── duplicate_finder.py  # sk-duplicates
    ├── csv_cli.py           # sk-csv
    ├── password_cli.py      # sk-password
    └── rename_cli.py        # sk-rename
```

Public re-exports:

- `swiss_knife` (top-level): `SafetyError`, `ValidationError`, `convert_keys_to_camel_case`, `get_env_bool`, `get_env_float`, `get_env_int`, `is_empty`, `is_not_empty`, `parse_bool`
- `swiss_knife.file_management`: `find_duplicates`, `bulk_rename`, `DuplicateFinder`, `BulkRenamer`
- `swiss_knife.text_processing`: `convert_csv`, `CSVConverter`
- `swiss_knife.automation`: `generate_password`, `PasswordGenerator`
- `swiss_knife.utilities`: 19 helpers including `parse_bool`, `is_empty`, `is_not_empty`, `get_env_int`, `get_env_float`, `get_env_bool`, `convert_keys_to_camel_case`, `decode_base64_text`, `is_uuid`, `is_http_status_code`, and more

## CLI Entry Points

Defined in `pyproject.toml` under `[project.scripts]`:

| Console script   | Module                              |
|------------------|-------------------------------------|
| `sk`             | `swiss_knife.cli.main`              |
| `sk-duplicates`  | `swiss_knife.cli.duplicate_finder`  |
| `sk-csv`         | `swiss_knife.cli.csv_cli`           |
| `sk-password`    | `swiss_knife.cli.password_cli`      |
| `sk-rename`      | `swiss_knife.cli.rename_cli`        |

All packaged CLIs support `-V` / `--version` (via `swiss_knife/cli/_common.py`). Use `sk --version` for the package version; per-tool commands print their own prog name with the same version.

## Top-level re-exports

`swiss_knife/__init__.py` re-exports a curated subset of utilities for convenience:

```python
from swiss_knife import parse_bool, is_empty, is_not_empty, get_env_int, get_env_float, get_env_bool, convert_keys_to_camel_case
```

The full set of `swiss_knife.utilities` helpers (19 total) includes `decode_base64_text`, `is_uuid`, `is_http_status_code`, `has_value`, `get_or_default`, `delete_if_present`, `is_true`, `is_false`, `is_numeric`, `to_camel_case`, `sanitize_metric_name`, `sanitize_header_name`, and the re-exported ones above.

## Versioning

- **Canonical version string:** `swiss_knife/__init__.py` → `__version__`
- **Build metadata:** `pyproject.toml` uses `dynamic = ["version"]` with `version = {attr = "swiss_knife.__version__"}`
- **Standalone scripts:** `scripts/_common.py` reads the same version from installed metadata or `swiss_knife/__init__.py`
- Bump only `__version__` in `__init__.py` when releasing; never duplicate a static version in `pyproject.toml`

## Optional Dependencies

| Extra   | Installs     | Purpose                          |
|---------|--------------|----------------------------------|
| `xml`   | `defusedxml` | Safer XML output for `sk-csv`    |
| `all`   | `defusedxml` | All optional runtime deps        |
| `dev`   | pytest, ruff, mypy, bandit, ... | Development only |

JSON conversion works on the base install. XML conversion also works without `defusedxml` but `[xml]` / `[all]` is recommended for hardened XML handling.

## Working Rules

- Read package metadata first: `pyproject.toml`, `swiss_knife/__init__.py`, and CLI modules under `swiss_knife/cli/`.
- Prefer `rg` and `rg --files` for discovery.
- Use `apply_patch` for file edits.
- Do not revert user changes or unrelated worktree modifications.
- Keep edits tightly scoped to the requested behavior.
- Use ASCII unless the file already requires Unicode.

## Verification

### End-user / PyPI smoke test (preferred for release validation)

Install like a stranger — outside the repo, in a fresh venv, from PyPI:

```bash
python3 -m venv /tmp/sk-test && /tmp/sk-test/bin/pip install 'swiss-knife-py[all]'

# Imports
/tmp/sk-test/bin/python -c "import swiss_knife; from swiss_knife.file_management import find_duplicates; from swiss_knife.text_processing import convert_csv; from swiss_knife.automation import generate_password"

# CLI help and version
/tmp/sk-test/bin/sk --help
/tmp/sk-test/bin/sk --version
/tmp/sk-test/bin/sk-duplicates --help
/tmp/sk-test/bin/sk-csv --help
/tmp/sk-test/bin/sk-password --help
/tmp/sk-test/bin/sk-rename --help

# Functional spot checks (use a temp directory)
/tmp/sk-test/bin/sk-password --length 16
/tmp/sk-test/bin/sk-csv /path/to/data.csv --format json -o /path/to/out.json
/tmp/sk-test/bin/sk-duplicates /path/to/dir
/tmp/sk-test/bin/sk-rename 'old' 'new' /path/to/dir --dry-run
```

As of 0.1.3, all of the above pass when installed from PyPI.

### Developer verification (in-repo)

```bash
pip install -e .[dev,all]
pytest
make ci          # lint + security + test-cov + build
make release-check
python3 -m build
python3 -m twine check dist/*
```

Install the built wheel into a fresh venv before end-to-end CLI checks when validating packaging changes.

## Testing Focus

- Prefer real CLI invocations through installed console scripts.
- Validate both success paths and error handling (missing paths, invalid input).
- Keep API checks aligned with what the installable package actually exports.
- Test suite lives in `tests/`; coverage threshold is 85% (`pyproject.toml`).

## Documentation Rules

- Separate installable package APIs from standalone repository scripts.
- PyPI install command is always `swiss-knife-py` (not `swiss-knife` or `swissknife`).
- Remove claims about non-existent package modules, extras, or CLI commands.
- Keep README, quickstart, installation, and API reference consistent with `swiss_knife/` contents.
- Authoritative references: `docs/cli-reference.md`, `docs/api-reference.md`, `docs/quickstart.md`, `docs/installation.md`, `docs/ARCHITECTURE.md`, `docs/DEVELOPMENT.md`.

## CI / Release

- CI (`.github/workflows/ci.yml`): matrix Python 3.8–3.12 via reusable `_test.yml` workflow, ruff, bandit, mypy (non-blocking), pytest with coverage; build + twine check on Python 3.12.
- Additional workflows: `security.yml` (Semgrep), `labeler.yml` (PR auto-labeling).
- Release (`.github/workflows/release.yml`): tag `v*` triggers test → build → PyPI publish → GitHub release with auto-generated changelog.
- Makefile targets: `dev-setup`, `install-dev`, `install-all`, `test`, `test-cov`, `test-fast`, `lint`, `format`, `security`, `typecheck`, `quality`, `build`, `validate`, `check-cli`, `ci`, `release-check`, `demo`, `clean`.
