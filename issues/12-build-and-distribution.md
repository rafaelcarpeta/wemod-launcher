Standalone .AppImage built with PyInstaller; replace .bat with binaries

Proposed by: marvin1099 — docs/14-build-and-distribution.md; github.com/DeckCheatz/wemod-launcher/discussions/258 (items 4, 5)

Distribute the launcher as a single PyInstaller-produced `.AppImage` so
end users no longer need to manage a Python virtualenv or install system
packages, with every Python dependency (PyQt6 included) bundled inside.
The Process Monitor — being a Windows PE for Wine — is built separately
from its own repo via CI into `monitor.exe` (PyInstaller, cross-compiled
or built on Windows) and downloaded by the launcher on demand. Wine,
Proton, graphics drivers, and game runtimes stay as host system
dependencies and are intentionally not bundled. The AppImage is
published per release via GitHub Actions alongside static
`metadata.json` for URLs and version info, and the self-contained
binary avoids sandbox-escape issues for Flatpak/Steam scenarios.

The same approach replaces the `.bat` files the current launcher drops
into Wine prefixes: write them in Python and compile to `.exe` via CI.
Batch files are brittle (whitespace, quoting, Wine path-escaping),
harder to debug than a real process with stdout/stderr, and can't
participate in the structured IPC and event model used by the monitor.
A compiled binary artefact for each in-prefix helper gives the launcher
real processes to spawn, observe, and tear down predictably.
