# Implementation Guide

## Overview

The launcher is a sequential pipeline: bootstrap core services, run action phases, show the troubleshooter if anything failed. Every phase is wrapped in a guard that catches exceptions, logs them with type and message, and shows a user-facing error notification. Non-fatal errors in one phase don't stop later phases from running.

---

## Bootstrap Sequence

### PathManager

The first object created. It computes XDG paths once:

- `~/.local/share/wand/` — persistent data (app binary, prefixes, login data, metadata)
- `~/.config/wand/` — user and auto-generated config files
- `~/.cache/wand/` — downloads, temp files, logs

No filesystem operations beyond checking if directories exist. Paths are strings, not `pathlib` objects — the manager centralizes all path logic so callers never construct paths themselves.

### LogManager

Created with a reference to PathManager so it knows where to write log files. Implements a typed event bus:

- `log.info(type, message)` → shorthand for `log.emit(type, "info", message)`
- `log.error(type, message)` → shorthand for `log.emit(type, "error", message)`
- `log.emit(type, level, message)` → full form, used for custom levels

Events are emitted to all subscribed handlers. By default there's a file handler (writes to `~/.cache/wand/launcher.log`) and a console handler. The interface can subscribe its own handler to display events in the UI. The log file header records the launcher version, Python version, platform, and invocation timestamp.

Subscribers can filter by type (e.g. only `launcher.flow.*`), level, or both. The troubleshooter subscribes to error-level events from the flow namespace to pre-populate its issue report.

### ArgManager

Wraps `sys.argv` once, early in bootstrap. Exposes parsed flags as attributes:

- `is_force_root_active` — whether `--force-root` was passed
- `is_cli` — whether `--cli` was passed
- `is_no_prompt` — whether `--no-prompt` was passed
- `has_post_update` — whether the launcher was re-invoked after a self-update
- Any remaining positional args (used for game exe path, prefix path, etc.)

ArgManager only parses CLI flags. It does not merge with config files or env vars — that's SettingsManager's job.

### SettingsManager

The unified settings layer. Construction order matters:

1. `SettingsManager(args)` — init from ArgManager only (CLI flags parsed but config not loaded yet)
2. Later, `settings.load_config()` — merges env vars and config files

Merge priority (highest wins): CLI args > env vars > config files > hardcoded defaults.

Config files are loaded from `~/.config/wand/`. The user-editable file is `config.json`. Auto-generated metadata is stored in `~/.local/share/wand/metadata.json` (version, URLs, download links, etc.). Settings are exposed as flat attributes (`settings.is_cli`, `settings.download_url`, etc.) — no nested dict access.

### Interface Detection

`detect_interface(settings, log)` returns either a `GUIInterface` (PyQt6) or `CLIInterface` instance. The decision:

- If `--cli` or `--no-prompt` flags are set → CLIInterface
- Otherwise → GUIInterface (default)

The interface implements a small protocol:

- `show_message(text)` — display a message to the user (modal dialog or print)
- `error_msg_and_log(type, text)` — log the type and text, then show the text
- Additional methods for progress, prompts, etc. (defined in the abstract base)

### Root Guard

`check_root(interface, settings)` runs before `settings.load_config()`. If `os.geteuid() == 0` and `settings.is_force_root_active` is False, it shows a message and calls `sys.exit(1)`. The interface is passed so the message is visible in both GUI and CLI mode. Config files are not loaded until after this check passes — no point reading config if we're about to exit.

### Step Runner

After bootstrap, a `StepRunner` is created with the four core objects (path_mgr, settings, interface, log). Every action phase goes through the runner, which wraps `step()` or `step_code()`:

- `step()` — catches exceptions, calls `interface.error_msg_and_log(type, msg)`, returns True on failure
- `step_code()` — same but returns `(failed, code)` for phases that produce an exit code

Boolean flags (p, s, i, lg) control which core objects get passed to the phase function. This keeps calls concise and makes the parameter contract explicit at the call site.

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

**Dev mode:**
- Runs `git pull` in the repository directory
- Does not reset --hard — preserves local changes
- Only triggers if the running version is a dev build (detected via version string or presence of `.git`)

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

1. Check if the exe is already present and the checksum matches
2. If missing or corrupted, download from the URL in `metadata.json`
3. Extract the archive to `~/.cache/wand/` then copy the exe to `~/.local/share/wand/bin/`
4. Verify the checksum of the extracted file

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

If the shared data already has files (from a previous run or another game), the sync preserves them — only new or changed files are copied.

### Monitor Launch

The last action phase. Replaces the game command with the monitor process.

The monitor is a separate binary that lives inside the Wine prefix (or is downloaded alongside the app). Its job is process lifecycle management:

1. Receive a `LaunchConfig` via TCP/JSON from the launcher
2. Start the app executable (wand.exe)
3. Start the game executable
4. Wait for the game to exit
5. If wand is still running after the game exits, send a terminate signal
6. Send a `session_complete` event to the launcher with the game's exit code
7. Exit

The launcher waits for the monitor's exit code and returns it as its own exit code. If the monitor cannot be started (missing binary, port in use, etc.), the phase reports failure and the troubleshooter runs.

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
