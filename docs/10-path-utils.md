# Path Utilities

XDG-aware path management for the launcher.

## Base Directories

| Purpose | Path | Env Override |
|---|---|---|
| Config | `$XDG_CONFIG_HOME/wand/` (default: `~/.config/wand/`) | `XDG_CONFIG_HOME` |
| Data | `$XDG_DATA_HOME/wand/` (default: `~/.local/share/wand/`) | `XDG_DATA_HOME` |
| Cache | `$XDG_CACHE_HOME/wand/` (default: `~/.cache/wand/`) | `XDG_CACHE_HOME` |

## Managed Paths

- Config dir: `config.json`, `metadata.json`, `source_values.json`
- Data dir: `wand_bin/Wand.exe`, `wand_bin/` (working dir), `login/` (login tokens), `prefixes.db`
- Cache dir: downloaded `.nupkg` files, temp downloads

## Session Directory

Each run creates `/tmp/wand-<pid>/` for (also possible as fixed dir like wand-launcher-tmp):
- Monitor stdout/stderr logs
- Crash reports
Cleaned up on exit.| `waring` | message | Return a waring |

## Wine Path Conversion

Convert Linux paths to Wine Z: paths (and inverted if need be):
```
/home/user/.local/share/wand/wand_bin/Wand.exe
  → Z:\home\user\.local\share\wand\wand_bin\Wand.exe
```
Used when passing paths to the monitor (which runs inside Wine).
