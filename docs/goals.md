# Project Goals & Direction

## Codebase & Architecture

- Structured, readable code with clear separation of concerns
- Group code by responsibility (paths, settings, logging, UI, steps)
- Clear internal APIs between components
- Python is the practical choice — already in use, performance isn't critical at startup

## CLI / Interface Modes

- Full non-interactive mode via CLI flags (`--cli`, `--no-prompt`)
- Unified interface layer — CLI (print/input) or GUI (PyQt6)
- Centralized user interaction instead of scattered prompts

## Build & Distribution

- PyInstaller-based build, packaged as AppImage
- Inside-Wine monitor is a standalone `.exe`, built via CI
- All libraries bundled — no sandbox escape issues, no venv needed
- Binary releases instead of source-only

## Process Monitor

- Config-driven process supervisor (declarative, not hardcoded)
- Multiple process lifecycle management (game + trainer)
- Event-driven model with structured IPC (TCP/JSON)
- Clean integration between Wine/Proton and the Linux host
- Extensible — not limited to a single tool

## Updates & Versioning

- Proper binary updater via GitHub Releases
- Structured migration system for breaking changes (config layout, data format)
- GitHub Actions: builds, metadata, tests, formatting

## Configuration & Environment

- Tiered config: CLI args → env vars → config file → defaults
- Consistent prefix handling between Proton and Wine (`pfx` normalization, symlinks)
- XDG-compliant paths everywhere

## Logging & Debugging

- Subscription/event-based logging — components emit structured events
- Standard log levels, optional event stream subscriptions
- Multiple handlers (console, file, UI) that process events differently
- Structured, contextual messages for debugging

## Path & Filesystem

- Dedicated path management with Unix ↔ Wine conversion utilities
- Symlink resolution, ownership handling, cache management
- Centralized, predictable filesystem operations

## Platform

- Container-compatible via AppImage
- "Wand launcher" — multi-tool, not tied to a single provider
