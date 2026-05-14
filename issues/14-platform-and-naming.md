Platform/container compatibility and rename to Wand Launcher upstream

Proposed by: marvin1099 — docs/16-platform-and-ecosystem.md; github.com/DeckCheatz/wemod-launcher/discussions/258 (items 13, 14)

Target `.AppImage` as the primary distribution format to sidestep most
Flatpak sandbox issues, while still being mindful of containerized
environments: Flatpak Steam requires resolving `STEAM_COMPAT_DATA_PATH`
and `STEAM_COMPAT_TOOL_PATHS` across filesystem boundaries, and
container runtimes (Distrobox, Toolbox) need host GPU and filesystem
access — the launcher should not assume it controls the entire
environment. The legacy `FROM_FLATPAK` env var is dropped since the
AppImage model makes it obsolete. System dependencies remain external
(Wine, Proton, game runtimes, graphics drivers, FUSE for AppImage
execution).

The project is also renamed from "WeMod Launcher" to "Wand Launcher" to
follow upstream naming and integrate more cleanly into the upstream
ecosystem. All code, config paths, documentation, binary names, and
env-var prefixes use `wand`/`WAND_` consistently — binary
`wand-launcher`, config `$XDG_CONFIG_HOME/wand/`, data
`$XDG_DATA_HOME/wand/`, cache `$XDG_CACHE_HOME/wand/`. A one-time
disruptive rename trades short-term churn for fewer naming oddities,
fewer divergence points with upstream, and a cleaner identity separate
from the WeMod brand.
