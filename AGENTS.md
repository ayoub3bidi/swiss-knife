# AGENTS.md

Repository guidance for agents working in this workspace.

## Scope

- The installable package is `swiss_knife/`.
- The standalone script trees are `automation/`, `convert/`, `file_management/`, `network_web/`, `system_utilities/`, `text_processing/`, and `utilities/`.
- The standalone script trees are not installed by `pip install swiss-knife-py` unless a script explicitly vendors its own requirements.

## Working Rules

- Read the package metadata first: `pyproject.toml`, `swiss_knife/__init__.py`, and the CLI modules under `swiss_knife/cli/`.
- Prefer `rg` and `rg --files` for discovery.
- Use `apply_patch` for file edits.
- Do not revert user changes or unrelated worktree modifications.
- Keep edits tightly scoped to the requested behavior.
- Use ASCII unless the file already requires Unicode.

## Package Surface

- Public package exports live under `swiss_knife/`.
- Current CLI entry points are defined in `pyproject.toml` under `[project.scripts]`.
- Documentation must not claim standalone scripts are pip-installed package APIs.

## Verification

- Build the package with `python3 -m build`.
- Check release artifacts with `python3 -m twine check dist/*`.
- Install the built wheel into a fresh virtual environment before end-to-end CLI checks.
- Run `pytest` from a dev install when validating code changes.

## Testing Focus

- Prefer real CLI invocations through the installed console scripts.
- Validate both success paths and error handling for CLI commands.
- Keep API checks aligned with what the installable package actually exports.

## Documentation Rules

- Separate installable package APIs from standalone repository scripts.
- Remove claims about non-existent package modules, extras, or CLI commands.
- Keep README, quickstart, installation, and API reference consistent with `swiss_knife/` contents.

