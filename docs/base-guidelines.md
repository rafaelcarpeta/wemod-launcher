# Docs: Wand Launcher flow draft

> All paths in this doc use their default locations.  
> If the corresponding XDG environment variable is set (`XDG_DATA_HOME`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`),  
> the paths resolve accordingly.

## The Main Flow

The main flow is simple — the launcher is essentially a fancy argument parser. Here's what happens:

### Bootstrap

- **SettingsManager** — basic init: parses `sys.argv` and computes XDG paths. No config files loaded yet.
- **LogManager** — takes settings (reads log path from it), starts the log file.
- **Interface** — detected from settings flags: PyQt6 by default, CLI if `--cli` or `--no-prompt`.
- **Root guard** — checks `os.geteuid()` and `--force-root`, exits early if running as root without the flag.
- **SettingsManager.load_all()** — loads global config (`config.json`), game config (`games.json`), and metadata. Merge priority: CLI args > env vars > game config > global config > hardcoded defaults.
- Enter the main execution block

Arg parsing and path computation are handled by SettingsManager internally — no separate ArgManager or PathManager modules. Settings is the single source for flags, paths, and config values throughout the launcher.

### Download the App

- Download and extract the app exe if missing
- See [Download the App](#download-the-app) for details

### Prefix Setup

- Make sure the prefix is set up (most complex task, irrelevant after the wand prefix is installed)
- See [Prefix Setup](#prefix-setup) for details

### Syncing App Data

- Link app data to the shared storage after prefix is ready
- See [Syncing App Data](#syncing-app-data) for details

### Monitor Launch

> The monitor is a separate binary in its own repository — this section covers
> the launcher side only. The launcher downloads `monitor.exe` from the
> monitor's GitHub releases, sends a `LaunchConfig` via TCP/JSON, and reads
> the exit code.

- Download `monitor.exe` from the monitor's GitHub releases
- Send a `LaunchConfig` via TCP/JSON with the game exe path, wand exe path, and lifecycle instructions
- Wait for the monitor to report `session_complete` with the game's exit code
- Return that exit code as the launcher's own exit code
- See [The Monitor Start File](#the-monitor-start-file) for details

### Troubleshooter

- Bring up a simple troubleshooter if wand didn't start
- All logs go to `~/.cache/wand/` (log level can be increased for debugging)
- Offers options like redownloading the prefix, redownloading wand, or deleting the prefix to start fresh
- By default this is a PyQt6 GUI with progress bars, buttons, and dialogs
- With `--cli` it falls back to text-based prompts and line-overwrite progress
- After the troubleshooter exits, the wand-launcher script exits

---

## Download the App

To use wand the app exe needs to be in place. Downloads and temporary caches go to `~/.cache/wand/`.

### Installing the App

- Check if the app exe exists
- If not, download the archive from the URL in `metadata.json`
- Verify the downloaded archive against its reported checksum (provided by the online repo)
- Extract to `~/.cache/wand/` then copy the app to `~/.local/share/wand/bin/` so all prefixes can use it
- The exe contains all app files (dependencies are handled separately during prefix setup)

---

## Prefix Setup

Once the app is downloaded, wand needs to be set up in the wine prefix. Config files live in `~/.config/wand/`, and updates and persistent storage use `~/.local/share/wand/`. This is the most complex part:

### Checking the Prefix

- Normalize prefix: move files from `pfx/` to `.` and delete `pfx`
- Normalize user: move from `drive_c/users/steamuser/` to `drive_c/users/$USER/` and delete `steamuser`
- Add symlinks: `pfx` → `.`, and in folder `drive_c/users/`; `steamuser` → `$USER`

- Check if the prefix already has wand installed
- Look for `.wand_installer` in the same folder as `drive_c`
- If found: prefix install is done — return to [The Main Flow](#the-main-flow)

### Scanning for Existing Prefixes

If `.wand_installer` is missing, scan the parent directory for a sibling prefix that has it:

1. Scan all sibling prefixes for `.wand_installer`, store results in `~/.local/share/wand/prefixes.json` and remove stale entries
2. Look up the best matching prefix in the database

Ask the user what to do (three options depend on how many valid prefixes exist):

- **Closest match** — copy the best matching prefix (only if one or more valid prefixes exist)
- **Download** — grab a wand-ready prefix from GitHub, unpack it (cached in `~/.cache/wand/`)
- **Second Closest Match** — auto-pick the next best prefix (only if exactly 2 valid prefixes exist)
- **List all** — pick from all valid prefixes (only if 3+ valid prefixes exist)
- **Build** - Download winetricks, run `winetricks -q sdl cjkfonts vkd3d dxvk2030 dotnet48` and add `.wand_installer` next to `system.reg`
- **Exit** — cancel

Return to [The Main Flow](#the-main-flow) after completion.

---

## Syncing App Data

After the prefix is set up, the app data needs to be linked to the shared storage at `~/.local/share/wand/`.

- Copy the app data folder to `~/.local/share/wand/login/`
- If the shared store already has data and the prefix also has data, prompt the user to pick which copy wins
- Symlink the app's data folder inside the prefix to that central `login` folder
- Now all games share the same app data — synced by design

### Packaging a Prefix

- Check if the prefix should be packaged into a zip
- Used when a prefix needs to be uploaded

---

## The Monitor Start File

The monitor is a separate binary (different repo). From the launcher's perspective:

- Download `monitor.exe` from the monitor's own GitHub releases (separate repo from both launcher and wand app)
- Send a structured `LaunchConfig` via TCP/JSON — defines game exe path, wand exe path, start order, dependencies, and shutdown rules
- Wait for the monitor to respond with `session_complete` containing the game's exit code
- Return that exit code as the launcher's own exit code

The monitor replaces the old bat file approach with a config-driven protocol. The launcher only worries about building the config and reading the result — the monitor handles all process lifecycle inside Wine/Proton.
