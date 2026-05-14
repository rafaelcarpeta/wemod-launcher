Wand.exe lifecycle: install, login symlink sync, and custom override

Proposed by: marvin1099 — docs/07-wand-lifecycle.md

The launcher manages the WeMod `Wand.exe` binary as a first-class
lifecycle: download to `$XDG_DATA_HOME/wand/wand_bin/`, fetch release
info from a `RELEASES` URL, and extract the latest package, skipping the
download if the user supplies a custom executable via `--wand-exe` or
`WAND_EXE`. Login tokens live in `$XDG_DATA_HOME/wand/login/` and are
synced into the Wine prefix via symlinks (not copies) so authentication
state is shared across prefixes without duplication. Static-but-
changeable values (Wand release URL, monitor download URL, launcher
repo, prefix repo, default user agent) live in a separate
`metadata.json` so URLs and patterns can be updated without shipping a
new code release.
