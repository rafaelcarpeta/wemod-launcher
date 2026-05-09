# Wand Launcher — Rewrite Blueprint

This repository defines the **goals, component boundaries, and known behaviors** for the Wand Launcher rewrite. Implementation lives in the `wand-full-rewrite` branch.

## Branch Strategy

| Branch | Purpose |
|---|---|
| `apis-and-protocols-for-rewrite` | **This branch.** General specs, goals, component contracts. No code. |
| `wand-full-rewrite` | Clean-slate implementation following these specs. |

## Core Goals

- **CLI-first design** — every operation accessible via terminal flags
- **Deterministic priority** — CLI flags > env vars > config file > defaults (never ambiguous)
- **Small modules** — every Python file < 100 lines; split if it grows
- **No persistent GUI** — only on-demand dialogs for interactive prompts
- **Explicit over implicit** — separator for unambiguous arg splitting
- **Defensive parsing** — raise on ambiguity; never guess silently
- **IPC to a monitor process** — launcher delegates process management
- **Monitor lives in its own repo** — separate project, separate release cycle
- **XDG base directory compliance** — config in `$XDG_CONFIG_HOME/wand`, data in `$XDG_DATA_HOME/wand`, cache in `$XDG_CACHE_HOME/wand`

## High-Level Components

### ArgParser ([doc](docs/01-arg-parser.md))
Public API that takes raw argv and returns structured fields. Internally handles:
- Flag extraction (arity system: 0=boolean, 1=value, -1=variadic)
- Game detection via internal multi-step scanner (URL → .exe → PE header → known binary → positional)
- CLI command detection ([doc](docs/12-cli-commands.md))
- Separator detection for unambiguous splitting
- Raises on ambiguous input

Game detection is **not** a separate public component — it's an internal detail of ArgParser.

### SettingsManager ([doc](docs/02-settings-manager.md))
- Resolves every setting with strict priority: CLI flag > env var > config file > default
- Covers: prefix path, wand executable, wand working dir, wand args, no-prompt mode, log level, log topics
- Single source of truth for "what value wins"
- Legacy env vars documented for reference

### ErrorManager / Error Hierarchy ([doc](docs/04-error-handling.md))
- Base error class with: message, recoverable flag, suggestion string
- Subclasses for each domain: arg parsing, config, database, network, prefix, IPC, migration
- Top-level catch in engine → log + dump crash report + return exit code

### LoggingManager ([doc](docs/05-logging.md))
- Event bus architecture: emit events, subscribe handlers
- Multiple handler types: file, console, crash reporter ring buffer
- Level system with threshold, range, and explicit set syntax
- Topic-based filtering with glob patterns
- Per-stream subscriptions for process stdout/stderr
- Structured event context

### PrefixManager ([doc](docs/06-prefix-management.md))
- Track Wine prefixes in a database
- Each prefix has: path, gamepath, wand-installed-status, timestamps
- Scan existing prefixes on disk, validate them, clean missing entries
- Support both downloading pre-built prefixes and installing to existing wineprefixes
- Prefix normalization (pfx symlink, Steam user symlink)

### Game-Prefix Association ([doc](docs/06-prefix-management.md))
- Track which game (executable path) was last used with which prefix
- Auto-resolve prefix on subsequent launches if game was seen before

### WandManager ([doc](docs/07-wand-lifecycle.md))
- Download Wand.exe to `$XDG_DATA_HOME/wand/wand_bin/`
- Sync login data via symlinks in `$XDG_DATA_HOME/wand/login/`
- Allow custom Wand executable override (mostly useful for testing)

### ConfigManager ([doc](docs/08-configuration.md))
- Load user config from `$XDG_CONFIG_HOME/wand/config.json`
- Merge with defaults, apply env var overrides
- Load metadata and static source values
- Old INI-format config (`wemod.conf`) documented for reference

### Monitor — separate repo ([doc](docs/09-monitor-contract.md))
- Windows PE running inside Wine
- Communicates with launcher via JSON-over-TCP
- Config-driven process definitions (declarative deps, startup/shutdown order)
- Event-driven lifecycle (start/exit/crash events, stdout streaming)
- Written to error fallback file inside prefix if TCP unavailable

### PathManager ([doc](docs/10-path-utils.md))
- XDG-aware path resolution
- Session file management (temp dir per run)
- Unix-to-Wine path conversion (Z: paths)

### UI Interface ([doc](docs/13-ui-interface.md))
- Abstract interface: show_message, show_error, confirm, choose, directory_picker, progress
- ProgressHandle with update/complete/fail
- CLI implementation (print/input)
- GUI implementation (PyQt6 dialogs only, no persistent window)
- `--no-prompt` flag auto-answers all prompts

## Flow Docs

- **Launch Flow** ([doc](docs/11-launch-flow.md)) — full sequence from CLI args to game session, with sequence diagram

## Build & Distribution ([doc](docs/14-build-and-distribution.md))

- PyInstaller produces `.AppImage` — self-contained, no virtualenv needed
- Monitor `.exe` built separately via CI in its own repo
- All Python deps bundled; Wine/Proton are system deps

## Updates & Versioning ([doc](docs/15-updates-and-versioning.md))

- Semver versioning tracked in `metadata.json`
- Self-updater: fetch latest release, download, replace, restart
- Migration manager for breaking changes (config, DB, directory layout)
- GitHub Actions: lint, test, build, publish on tag

## Platform & Ecosystem ([doc](docs/16-platform-and-ecosystem.md))

- Flatpak/container considerations
- Consistent "Wand" naming across binary, paths, and docs
- System dependencies (Wine, Proton, FUSE) are not bundled

## Known Input Examples

### Steam launch chain
```
['/home/user/.local/share/Steam/ubuntu12_32/steam-launch-wrapper',
 '--',
 '/home/user/.local/share/Steam/ubuntu12_32/reaper',
 'SteamLaunch', 'AppId=3527290',
 '--',
 '/home/user/.local/share/Steam/steamapps/common/SteamLinuxRuntime_sniper/_v2-entry-point',
 '--verb=waitforexitandrun',
 '--',
 '/usr/share/steam/compatibilitytools.d/proton-cachyos-slr/proton',
 'waitforexitandrun',
 '/home/user/.local/share/Steam/steamapps/common/PEAK/PEAK.exe']
```

Key observations:
- Multiple `--` separators exist inside the chain (they're Steam's, not the launcher's)
- The launcher needs its own distinct separator (e.g. `--wand--`)
- Infrastructure tools: `reaper`, `proton`, `waitforexitandrun`
- Game is the last `.exe` in the chain

### Lutris launch chain
```
wine game.exe +arg1
```

### CLI-only usage
```
wand-launcher --help
wand-launcher --version
```

## Module Size Rule

Every `.py` file must stay **under 100 lines**. If a module exceeds this:
1. Split into a package with sub-modules
2. Keep each sub-module under 100 lines
3. Re-export everything from `__init__.py`
