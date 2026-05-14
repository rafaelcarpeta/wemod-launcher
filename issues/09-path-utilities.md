XDG-aware path utilities with Unix↔Wine Z: conversion and symlink helpers

Proposed by: marvin1099 — docs/10-path-utils.md; github.com/DeckCheatz/wemod-launcher/discussions/258 (item 12)

Centralize all filesystem layout into a dedicated `paths` module that
respects `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, and `XDG_CACHE_HOME`
(defaulting to `~/.config/wand/`, `~/.local/share/wand/`,
`~/.cache/wand/`) and owns the canonical locations for `config.json`,
`metadata.json`, `source_values.json`, `wand_bin/`, `login/`,
`prefixes.db`, and cached downloads. Each run also gets a session
directory under `/tmp/wand-<pid>/` (or a fixed `wand-launcher-tmp`) for
monitor stdout/stderr logs and crash reports, cleaned up on exit.

The same module exposes Unix↔Windows path conversion for Wine's Z:
drive (e.g. `/home/user/.../Wand.exe` ↔ `Z:\home\user\...\Wand.exe`),
symlink dereferencing, and the filesystem operations needed for prefix
normalization. Centralizing this avoids the scattered, error-prone
path-mangling logic that currently lives across the launcher and is a
common source of Wine-side bugs (wrong slashes, missing escapes, broken
symlinks), giving the in-Wine monitor a single canonical form for any
path the launcher hands it.
