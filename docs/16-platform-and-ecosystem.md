# Platform & Ecosystem

Considerations for running the launcher across different environments.

## Container / Flatpak Compatibility

The launcher targets `.AppImage` as the primary distribution format, which avoids most Flatpak sandbox issues. However, when running inside or alongside containerized environments:

- **Flatpak Steam**: access `STEAM_COMPAT_DATA_PATH` and `STEAM_COMPAT_TOOL_PATHS` from the host — the launcher may need to resolve these through Flatpak's filesystem boundaries
- **Container runtimes (Distrobox, Toolbox)**: Wine/Proton need access to the host's GPU and filesystem — the launcher should not assume it controls the entire environment
- **No `FROM_FLATPAK` env var** — the `.AppImage` target makes this obsolete

## Naming

The project has migrated from "WeMod Launcher" to **Wand Launcher** to follow upstream naming. All references in code, config paths, documentation, and binary names use "wand" consistently:
- Binary: `wand-launcher`
- Config dir: `$XDG_CONFIG_HOME/wand/`
- Data dir: `$XDG_DATA_HOME/wand/`
- Cache dir: `$XDG_CACHE_HOME/wand/`

## System Dependencies

The launcher expects these to be available on the host:
- Wine / Proton (managed externally by Steam, Lutris, or the user)
- Standard XDG base directory support
- FUSE (for AppImage execution)

Not bundled: Wine, Proton, game runtimes, graphics drivers.
