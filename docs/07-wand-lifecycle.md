# Wand Lifecycle

Wand.exe (by WeMod) is the core application managed by the launcher.

## Installation

- Download Wand.exe to `$XDG_DATA_HOME/wand/wand_bin/`
- Fetch release info from a URL (RELEASES file)
- Download and extract the latest package
- Skip if custom Wand executable is provided via flag/env

## Login Data Sync

- Login tokens live in `$XDG_DATA_HOME/wand/login/`
- Synced into the Wine prefix via **symlinks** (not copies)
- Ensures Wand.exe is authenticated inside Wine without duplicating data

## Custom Wand

If `--wand-exe` flag or `WAND_EXE` env var is set:
- Use the provided executable directly, for testing

## Source Values

Static but changeable info (URLs, repos, patterns) lives in a dedicated file (e.g. `metadata.json`). Things that go there:
- Wand release URL and download base
- Monitor download URL
- Launcher GitHub repo
- Prefix download repo
- Default user agent string
