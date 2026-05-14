SettingsManager with strict CLI > env > config > default priority chain

Proposed by: marvin1099 — docs/02-settings-manager.md

Introduce a `SettingsManager` that resolves every launcher setting through
a single, predictable priority order: CLI flag, then environment variable,
then config file, then hardcoded default or auto-detect. It centralizes
resolution of the Wine prefix path, Wand executable and working dir, Wand
args, no-prompt mode, log level, and log topics, while also mapping a
fixed set of `WAND_*` env vars onto config paths with case-insensitive
boolean coercion (`"1"`, `"true"`, `"yes"` → True). The design explicitly
catalogs legacy env vars from the previous launcher
(`STEAM_COMPAT_TOOL_PATHS`, `STEAM_COMPAT_DATA_PATH`, `WINEPREFIX`,
`TROUBLESHOOT`, `SCANFOLDER`, `REPO_STRING`, `WAIT_ON_GAMECLOSE`,
`GAME_FRONT`, `NO_EXE`, etc.) and classifies each as keep, maybe, drop, or
evaluate so the rewrite has a clean migration boundary instead of carrying
historical baggage forward by accident.
