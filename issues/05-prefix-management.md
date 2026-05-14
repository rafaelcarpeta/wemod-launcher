Wine prefix tracking DB with scan, validate, clean, and normalize ops

Proposed by: marvin1099 — docs/06-prefix-management.md

Track every Wine prefix in a local database keyed by its path on disk,
with fields for the wand-installed tag, last-validated timestamp, and
created/updated timestamps. The launcher exposes scan (detect prefixes
and game executables in `drive_c/`), validate (mark prefixes that no
longer exist on disk), clean (purge missing entries), show, list, and
normalize operations — normalize ensures a consistent layout where `pfx`
is a symlink to `.` and `drive_c/users/<steamuser>` is a symlink to the
current Linux user so login/wallet data is shared across prefixes.

Prefixes can be sourced via download (pre-built from a release repo),
build (install into an existing Wine prefix without creating a new one),
Steam env vars (`STEAM_COMPAT_DATA_PATH`/`WINEPREFIX`), or manual
`--prefix`. The DB tracks which game executable was last launched with
which prefix so subsequent launches of the same game auto-resolve the
prefix when none is specified, eliminating the env-var dance the current
launcher requires.
