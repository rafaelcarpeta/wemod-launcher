Self-updater with ordered migrations and GitHub Actions release pipeline

Proposed by: marvin1099 — docs/15-updates-and-versioning.md; github.com/DeckCheatz/wemod-launcher/discussions/258 (items 9, 10)

Ship the launcher with a semver-tracked self-updater that fetches the
latest version from GitHub Releases, compares against the current version
in `metadata.json`, prompts the user (or auto-updates under
`--no-prompt`), downloads the new `.AppImage`, replaces the current
binary, and restarts — skippable via config or `--no-update`. Breaking
changes in config format, directory layout, or the prefix DB schema are
handled by a numbered, ordered migration manager
(`001_initial`, `002_new_config_format`, …) that runs automatically on
detecting an older version and can move files, restructure XDG
directories, transform `config.json`, and update the prefix DB schema,
with rollback support where feasible. Auto-generated `metadata.json`
tracks `version`, `channel` (stable/beta), `upstream`, `update_url`, and
`migration_version`.

A GitHub Actions pipeline removes all release toil: every push/PR runs
syntax checks, lint, auto-formatting enforcement, and the full unit test
suite (201+ tests). On tagged releases, CI builds the launcher
`.AppImage`, builds `monitor.exe` from the monitor repo, publishes the
release to GitHub, and updates `metadata.json` so the in-app updater
sees the new version immediately. This prevents drift between code and
metadata and gives contributors fast feedback on formatting and tests.
