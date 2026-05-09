# SettingsManager

Central resolution of all launcher settings with a strict priority chain.

## Priority

**CLI flag > environment variable > config file > hardcoded default / auto-detect**

## Settings It Resolves

| Setting | Sources (in priority order) | Notes |
|---|---|---|
| Prefix path | `--prefix` flag → `STEAM_COMPAT_DATA_PATH/pfx` → `WINEPREFIX` | Game-prefix association may also apply |
| Wand executable | `--wand-exe` flag → `WAND_EXE` env → auto-detect in data dir | |
| Wand working dir | `--wand-working-dir` flag → `WAND_WORKING_DIR` env → auto-detect | |
| Wand args | `--wand-args` flag only | Normalized from string → list |
| No-prompt mode | `--no-prompt` / `--noconfirm` flags (aceept all defaults, download wand and prefix) | |
| Log level | `--log-level` flag | |
| Log topics | `--log-topic` flag | |

## Env Overrides for Config

The following env vars override config file values directly when set:

| Env var | Config path | Type |
|---|---|---|
| `WAND_STEAM_COMPAT` | `paths.steam_compat` | string |
| `WAND_WINE_PREFIX` | `paths.wine_prefix` | string |
| `WAND_SCAN_FOLDER` | `paths.scan_folders` | list of one |
| `WAND_REPO` | `upstream.repo` | string |
| `WAND_PREFIX_REPO` | `upstream.prefix_repo` | string |
| `WAND_TROUBLESHOOT` | `features.troubleshooter` | bool |
| `WAND_NO_EXE` | `features.skip_exe_validation` | bool |
| `WAND_GAME_FRONT` | `features.pre_launch_command` | string |
| `WAND_WAIT_ON_GAMECLOSE` | `features.early_exit_timeout` | int |
| `WAND_VERBOSE` | `debug.verbose` | bool |
| `WAND_PACKAGE_PREFIX` | `debug.package_prefix` | bool |

Bool coercion: `"1"`, `"true"`, `"yes"` (case-insensitive) → True.

## Old Env Variables (Legacy Reference)

These existed in the previous launcher version. Not all need to be preserved — evaluate each for the rewrite:

| Old Variable | Config Equivalent | Purpose | Keep? |
|---|---|---|---|
| `STEAM_COMPAT_TOOL_PATHS` | — | Proton installation dirs (set by Steam) | Yes — runtime env |
| `STEAM_COMPAT_DATA_PATH` | — | Game prefix path (set by Steam) | Yes — runtime env |
| `WINEPREFIX` | — | Wine prefix path | Yes — fallback |
| `WINE_PREFIX_PATH` | — | External runner prefix | Maybe |
| `WINE` | — | Wine executable path | Maybe |
| `TROUBLESHOOT` | `features.troubleshooter` | Enable/disable troubleshooter | Yes |
| `SELF_UPDATE` | — | Allow auto-update | Evaluate |
| `WEMOD_LOG` | — | Log file path | LoggingManager handles this |
| `SCANFOLDER` | `paths.scan_folders` | Prefix scan directory | Yes |
| `NO_EXE` | `features.skip_exe_validation` | Skip game EXE validation | Yes |
| `REPO_STRING` | `upstream.repo` / `upstream.prefix_repo` | GitHub user/repo | Yes |
| `WAIT_ON_GAMECLOSE` | `features.early_exit_timeout` | Timeout for close dialog (seconds) | Yes |
| `GAME_FRONT` | `features.pre_launch_command` | Pre-game command (JSON array) | Yes |
| `PACKAGEPREFIX` | `debug.package_prefix` | Package prefix as ZIP | Evaluate |
| `FORCE_UPDATE_WEMOD` | — | Force Wand redownload | Evaluate |
| `FROM_FLATPAK` | — | Running from Flatpak host | No — .AppImage target |
