# Build & Distribution

The launcher is distributed as a standalone binary — no source builds or virtualenvs for end users.

## Build Tool

- **PyInstaller** produces a single `.AppImage` from the Python source
- The Process Monitor (Windows PE for Wine) is built separately in its own repo via CI

## AppImage

- Bundles all Python dependencies — no system Python packages required at runtime
- No virtual environment needed; the binary is self-contained
- Avoids sandbox escape issues by shipping everything in one package
- Built per release via GitHub Actions

## Process Monitor .exe

- The monitor component runs inside the Wine prefix as a Windows executable
- Built from its own repository via CI into a `.exe` file
- Distributed alongside the launcher as a downloadable artifact
- Written in Python, packaged with PyInstaller (cross-compiled or built on Windows)

## Release Artifacts

| Artifact | Source | Distribution |
|---|---|---|
| `wand-launcher.AppImage` | Launcher repo | GitHub Releases |
| `monitor.exe` | Monitor repo | Downloaded by launcher on demand |

## What Gets Bundled

- All Python source files
- All third-party dependencies (PyQt6, etc.)
- Static metadata (`metadata.json`) with URLs and version info
- **Not bundled**: Wine, Proton, or game runtimes — those are system dependencies

## Versioning

- Follows the launcher's own version (see Updates & Versioning)
- Monitor version is tracked independently but should stay compatible with the launcher version range
