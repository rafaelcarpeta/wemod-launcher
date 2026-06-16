# Implementation Guide

## Overview

The launcher is a sequential pipeline: bootstrap core services, run action phases, show the troubleshooter if anything failed. Every phase is wrapped in a guard that catches exceptions, logs them with type and message, and shows a user-facing error notification. Non-fatal errors in one phase don't stop later phases from running.

## Initial File Structure

Relative to `src/wand_launcher/`:

```
./__init__.py
./__main__.py                  # python -m wand_launcher → launcher.main()
./launcher.py                  # bootstrap → _run_flow() → troubleshooter
./core/__init__.py
./core/guards.py               # step(), step_code(), check_root
./core/runner.py               # StepRunner (step/step_code convenience)
./core/settings.py             # SettingsManager (args + paths + config merge)
./logging/__init__.py
./logging/event_bus.py         # LogManager with typed emit/subscribe
./logging/handlers.py          # File, console, UI log handlers
./migrations/__init__.py       # apply_migrations
./migrations/...               # individual migration scripts
./monitor/__init__.py          # launch_monitor
./monitor/protocol.py          # LaunchConfig schema, session_complete
./monitor/ipc/__init__.py
./prefixes/__init__.py
./prefixes/manager.py          # setup_prefix (orchestrator)
./prefixes/scanner.py          # scan sibling prefixes
./prefixes/matcher.py          # best-match logic
./prefixes/builder.py          # winetricks-based build
./prefixes/downloader.py       # download pre-built prefix
./troubleshooter/__init__.py   # run_troubleshooter
./troubleshooter/...           # GUI/CLI variants
./ui/__init__.py
./ui/detect.py                 # detect_interface
./ui/base.py                   # abstract Interface protocol
./ui/cli.py                    # CLIInterface
./ui/gui/__init__.py
./ui/gui/app.py
./ui/gui/main_window.py
./ui/gui/dialogs.py
./ui/gui/progress.py
./updates/__init__.py          # update_if_needed
./updates/binary.py            # AppImage/production updater
./updates/dev.py               # git-pull source updater
./utils/__init__.py
./utils/download.py            # unified download service
./utils/path_utils.py          # Unix↔Wine path conversion, symlink resolution
./wand/__init__.py
./wand/installer.py            # ensure_app (download & verify archive)
./wand/data_sync.py            # sync_app_data (login/ dir symlink)
```

> This is the initial file structure and is subject to change based on project needs and scope.

---

## Bootstrap Sequence

The bootstrap follows this order:

1. **SettingsManager** — basic init (arg parsing + base paths)
2. **LogManager** — takes settings (reads log path from it)
3. **Interface** — detected from settings
4. **Root guard** — uses settings + interface
5. **SettingsManager.load_all()** — config files, env vars, metadata
6. **StepRunner** — wraps the three remaining objects (settings, interface, log)

### SettingsManager (First — Basic Init)

The first object created. On init it handles two things that were previously separate modules:

**Arg parsing:** Wraps `sys.argv` once. Currently exposes a small set of flags:

- `is_force_root_active` — whether `--force-root` was passed
- `is_cli` — whether `--cli` was passed
- `is_no_prompt` — whether `--no-prompt` was passed
- `has_post_update` — whether the launcher was re-invoked after a self-update
- Positional args (game exe path, prefix path, etc.)

Most flags are not yet finalised — future args will be added as settings require them. `--help` support is an optional goal still under evaluation.

**Path computation:** Computes XDG paths:

- `settings.data_dir` → `~/.local/share/wand/`
- `settings.config_dir` → `~/.config/wand/`
- `settings.cache_dir` → `~/.cache/wand/`
- Derived paths: `log_path`, `bin_dir`, `login_dir`, `metadata_path`, `prefixes_db_path`

Paths are strings, not `pathlib` objects. No filesystem operations happen at init.

SettingsManager does **not** load config files yet — that happens after the root guard. The basic init provides just enough (args + base paths) for LogManager and interface detection to function.

### LogManager (Second)

Created with a reference to **settings** (not a separate PathManager). Reads `settings.log_path` (`~/.cache/wand/launcher.log`) and writes the file header there. Implements a typed event bus:

- `log.info(type, message)` → shorthand for `log.emit(type, "info", message)`
- `log.error(type, message)` → shorthand for `log.emit(type, "error", message)`
- `log.emit(type, level, message)` → full form, used for custom levels

Events are emitted to all subscribed handlers. By default there's a file handler (writes to the log path) and a console handler. The interface can subscribe its own handler to display events in the UI. The log file header records the launcher version, Python version, platform, and invocation timestamp.

Subscribers can filter by type (e.g. only `launcher.flow.*`), level, or both. The troubleshooter subscribes to error-level events from the flow namespace to pre-populate its issue report.

### Interface Detection (Third)

`detect_interface(settings, log)` returns either a `GUIInterface` (PyQt6) or `CLIInterface` instance. The decision:

- If `--cli` or `--no-prompt` flags are set → CLIInterface
- Otherwise → GUIInterface (default)

The abstraction auto-routes to the correct implementation. Each interface lives in its own file and implements a shared protocol. More interface types may be added later.

The interface protocol currently includes:

- `show_message(text)` — display a message to the user (modal dialog or print)
- `error_msg_and_log(type, text)` — log the type and text, then show the text
- Additional methods for progress, prompts, etc. (defined in the abstract base)

### Root Guard (Fourth)

`check_root(interface, settings)` runs before `settings.load_all()`. If `os.geteuid() == 0` and `settings.is_force_root_active` is False, it shows a message and calls `sys.exit(1)`. The interface is passed so the message is visible in both GUI and CLI mode. Config files are not loaded until after this check passes — no point reading config if we're about to exit.

### SettingsManager.load_all() (Fifth)

After the root guard passes, the full settings stack is loaded:

1. **Global config** — `~/.config/wand/config.json`, user-editable, general launcher settings
2. **Game config** — `~/.config/wand/games.json`, maps game paths (as IDs) to per-game overrides. A game may have no entry at all, partial settings, or full overrides.
3. **Metadata** — `~/.local/share/wand/metadata.json`, auto-generated (version, URLs, download links, user agent, etc.)

Merge priority (highest wins):
CLI args > env vars > game config > global config > hardcoded defaults.

Settings are exposed as flat attributes (`settings.is_cli`, `settings.download_url`, etc.) — no nested dict access. Metadata values are available through settings but are read-only — they can only be changed via the manifest and are not meant to be user-edited.

### Step Runner (After Bootstrap)

After bootstrap, a `StepRunner` is created with the three core objects (settings, interface, log). Every action phase goes through the runner, which wraps `step()` or `step_code()`:

- `step()` — catches exceptions, calls `interface.error_msg_and_log(type, msg)`, returns True on failure
- `step_code()` — same but returns `(failed, code)` for phases that produce an exit code

All three objects are always passed — every phase receives `(settings, interface, log)` consistently. Phase functions access paths through the settings object and may show messages or progress via the interface.

---

## Action Phases

### Updater

Checks for and applies launcher self-updates. Two modes:

**Production (AppImage):**
- Fetches the latest release metadata from GitHub Releases API
- Compares the published version against the running version (embedded in the AppImage metadata)
- If a newer version exists, downloads the AppImage to `~/.cache/wand/` and swaps it with the current binary
- A post-update marker is set so the re-invoked launcher knows an update just happened
- The swap is atomic: download to temp, rename over old, then re-exec

**Run from source mode:**
- Detected by running from a git repository (no AppImage, no binary release)
- Runs `git pull` in the repository directory — only makes sense in a git context
- Does not reset --hard — preserves local changes

If the network is unreachable, the updater logs the error and continues silently — a failed update is not a fatal error.

### Migrations

Checks `~/.local/share/wand/metadata.json` for a stored schema version and compares it against the expected version bundled with the launcher. If they differ, pending migrations run in order.

Each migration is a function that receives `settings` and `log`. Migrations can:

- Move or restructure files and directories (e.g., old config layout → new XDG layout)
- Update config file formats (e.g., ini → JSON)
- Transform the prefix database schema
- Delete deprecated cache files

Migrations are idempotent where possible. If a migration fails, the error is logged and the phase reports failure — the launcher cannot safely continue with an unknown schema version.

After all migrations succeed, `metadata.json` is updated with the current schema version. The file also stores the launcher version, download URLs, user agent string, and other auto-generated config.

### App Install

Ensures the app exe exists at `~/.local/share/wand/bin/`. The logic:

1. Check if the exe is already present
2. If missing, download the archive from the URL in `metadata.json`
3. Verify the downloaded archive against its reported checksum (the checksum is provided by the online repo alongside the download link)
4. Extract to `~/.cache/wand/` then copy the exe to `~/.local/share/wand/bin/`

Checksum verification is done on the archive, not the extracted file — the online repo provides the archive checksum alongside the download link. Verifying the extracted binary would require pre-generating checksums for every version, storing them in the manifest, and keeping them in sync — it's simpler and sufficient to just verify the archive.

Downloads use the unified download service (see Utilities section). The app exe is shared across all prefixes — it's installed once and every prefix uses the same binary.

### Prefix Setup

The most complex phase. Goal: ensure the Wine prefix has the app installed and ready.

**Step 1: Normalize the prefix**
- If a `pfx/` subdirectory exists, move all files and folders up one level, delete the empty `pfx/`, and create a symlink `pfx → .`
- If `drive_c/users/steamuser/` exists, move contents to `drive_c/users/$USER/`, delete `steamuser`, and create a symlink `steamuser → $USER`
- These normalizations handle the difference between Steam Proton prefixes (which use `pfx/` and `steamuser`) and standalone Wine prefixes

**Step 2: Check for existing installation**
- Look for `.wand_installer` marker in the same folder as `drive_c`
- If found, the prefix is ready — skip to data sync

**Step 3: Scan sibling prefixes**
Walk the parent directory looking for other prefixes that have `.wand_installer`. For each found prefix, record:

- Path
- App version installed
- Wine version used
- OS architecture (win32/win64)
- Any additional components installed

Results are cached in `~/.local/share/wand/prefixes.json`. Stale entries (prefix directories that no longer exist) are removed on each scan.

**Step 4: Match or build**

Present options to the user (varies based on how many valid prefixes were found):

- **Closest match** — copy the best-matching sibling prefix. Matching considers app version (exact match preferred), Wine version, and architecture.
- **Second closest** — auto-pick the next best if exactly 2 valid prefixes exist (skips the prompt)
- **Download** — fetch a pre-built prefix from GitHub Releases, extract to `~/.cache/wand/`, then move into place
- **List all** — let the user pick from all valid prefixes (shown when 3+ exist)
- **Build** — download winetricks, run: `winetricks -q sdl cjkfonts vkd3d dxvk2030 dotnet48`, then write `.wand_installer` next to `system.reg`
- **Exit** — cancel the whole flow

**Step 5: Post-setup**
After the prefix is ready (copied, downloaded, or built), the `.wand_installer` marker is written if not already present. The prefix path is stored for the data sync and monitor phases.

### Data Sync

After the prefix is ready, app data needs to be shared across all games.

**Step 1: Create the shared data directory**
`~/.local/share/wand/login/` — this is the central app data store. If it doesn't exist, create an empty one.

**Step 2: Sync prefix data to shared storage**
Copy the app data folder from inside the prefix to `~/.local/share/wand/login/`. This is a one-time copy — subsequent runs use the existing shared data.

**Step 3: Symlink back**
Remove the app data folder inside the prefix and replace it with a symlink pointing to `~/.local/share/wand/login/`. Now all games that use this launcher share the same app data — logins, settings, and cached data are synchronized by design.

If both the prefix app data and the shared `login/` directory already have content (e.g. from a previous game), the launcher prompts the user to resolve the conflict: use the current game account (overwrites the shared store), use the existing shared data (overwrites the prefix copy), or exit.

### Monitor Launch

The last action phase. From the launcher's perspective:

1. Download the monitor binary from the monitor's own GitHub releases (separate repo from both the launcher and the wand app)
2. Send a `LaunchConfig` via TCP/JSON containing the game exe path, wand exe path, and lifecycle instructions (start order, dependencies, shutdown rules)
3. Wait for the monitor to report `session_complete` with the game's exit code
4. Return that exit code as the launcher's own exit code

The monitor is a separate binary and lives in its own repository — this section only covers the launcher side of the interaction. If the monitor cannot be started (missing binary, port in use, etc.), the phase reports failure and the troubleshooter runs.

---

## Troubleshooter

Always runs, regardless of whether the flow succeeded. Two modes:

**GUI (default):** PyQt6 window with tabs:
- Status overview (which phases passed/failed)
- Log viewer (filterable, searchable)
- Action buttons: retry prefix setup, redownload app, delete prefix and start fresh
- Report generation (copies recent logs and system info to clipboard)

**CLI:** Text-based prompts with the same options. Progress bars use line-overwrite (carriage return) for clean output. The troubleshooter can be skipped entirely with `--no-prompt` — in that mode it only logs and exits.

The troubleshooter subscribes to error-level log events during the flow run, so by the time it opens it already knows what went wrong.

---

## Utilities

### Download Service

Unified download function used by the updater, app installer, and prefix downloader:

- User-Agent rotation for GitHub API calls
- Automatic retry with exponential backoff (3 retries, 2s base delay)
- Progress reporting via optional callback
- Checksum verification after download (SHA-256)
- Resume support for large downloads (range requests)
- Cache management: downloads go to `~/.cache/wand/`, cleaned up after extraction

### Path Utilities

- **Unix ↔ Wine path conversion:** `/home/user/.wine/drive_c/...` ↔ `C:\...`
- **Symlink resolution:** resolve real paths through symlink chains
- **Prefix normalization:** detect and fix `pfx/` and `steamuser` layouts
