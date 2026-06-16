# Docs: Wand Launcher flow draft

> All paths in this doc use their default locations.  
> If the corresponding XDG environment variable is set (`XDG_DATA_HOME`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`),  
> the paths resolve accordingly.

## The Main Flow

The main flow is simple — the launcher is essentially a fancy argument parser. Here's what happens:

### Bootstrap

- Run root checks and resolve any pending updates
- Migration manager checks the schema version in `~/.local/share/wand/metadata.json` and runs pending migrations if needed
- Initialize the **SettingsManager** — a unified interface over CLI args, environment variables, config files, and XDG paths. Everything reads settings from here.
- Detect the user interface — PyQt6 by default, CLI if `--cli` or `--no-prompt` flags are set
- Enter the main execution block

### Argument Parsing

- The ArgManager (part of SettingsManager) wraps `sys.argv` once
- Analyze the arguments for wine/proton to find the target game

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

> The monitor process will live in a separate repository — it's a standalone
> binary that communicates via TCP/JSON. The launcher only needs to launch it
> and read its exit code.

- Replace the command to run the monitor instead of the game
- Pass the game exe path to the monitor via IPC as JSON
- Run the monitor with the wine tool (proton in steam) which receives the game args
- The monitor starts both the game and wand, then exits
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
- If not, run the setup — downloads and extracts the app to `~/.local/share/wand/bin/` so all prefixes can use it
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
- If it doesn't exist, create an empty folder there
- Symlink the app's data folder inside the prefix to that central `login` folder
- Now all games share the same app data — synced by design

### Packaging a Prefix

- Check if the prefix should be packaged into a zip
- Used when a prefix needs to be uploaded

---

## The Monitor Start File

The monitor is minimal — its job is process management inside the Wine/Proton environment:

- Receive a `LaunchConfig` via TCP from the launcher
- The config defines which processes to start, in what order, and dependency rules
- Connect to the launcher on the given port
- Start wand.exe (or another app defined in the config)
- Start the game executable and wait
- On game exit, send a `session_complete` event to the launcher
- The launcher cleans up and the monitor exits

This replaces the old bat file approach. Instead of a hardcoded batch script, the monitor uses a config-driven system where the launcher sends a structured `LaunchConfig` via JSON over TCP. This means the monitor is not limited to wand — it can manage any set of processes with proper lifecycle handling, dependencies, and startup order.
