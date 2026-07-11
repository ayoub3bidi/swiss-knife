# Roadmap

Future ideas and planned improvements for Swiss Knife. Items here are not commitments — they are candidates for future releases.

## CLI Improvements

- Shell completion support (bash, zsh, fish)
- Man page generation
- **Breaking change candidate:** Subcommand-based `sk` interface (e.g. `sk duplicates`, `sk csv`) — would replace the current flat multi-binary design (`sk-duplicates`, `sk-csv`, etc.), requiring changes to all CLI scripts, automation, and documented examples. Requires a major version bump and deprecation period if pursued. The current `sk` entry point only exposes `--version` and `--help`; a subcommand model would give it real dispatching value.

## Packaging

- Docker image for isolated CLI usage
- Conda-forge package
- Platform-specific wheels with native extensions for performance-critical tools

## New Modules

- Configuration file management
- Text diff / merge utilities
- Log file analysis tools

## Developer Experience

- Plugin architecture for third-party extensions
- Configuration file support for user preferences
- Improved type stubs for IDE integration

## Monitoring & Observability

- Optional metrics collection for CLI usage (opt-in)
- Structured logging with configurable verbosity

## See Also

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) — current design and structure
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute
