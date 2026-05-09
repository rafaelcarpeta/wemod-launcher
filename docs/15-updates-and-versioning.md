# Updates & Versioning

The launcher ships with a self-update mechanism and a structured migration system.

## Version Management

- Launcher version follows semver (major.minor.patch)
- Current version is tracked in `metadata.json` (auto-generated)
- Upstream version info (latest available) is fetched from GitHub Releases

## Updater

On launch (or via a dedicated CLI command), the launcher can check for updates:

1. Fetch latest version from GitHub Releases
2. Compare with current version from `metadata.json`
3. If newer: prompt user (or auto-update in --no-prompt mode)
4. Download new `.AppImage`
5. Replace current binary and restart

Update can be skipped via configuration or `--no-update` flag.

## Migration Manager

Breaking changes (config format, directory layout, database schema) are handled by a migration system:

- Migrations are numbered and ordered (e.g. `001_initial`, `002_new_config_format`)
- Each migration can: move files, update directory structures, transform config JSON, modify the prefix database
- Run automatically when the launcher detects an older version
- Rollback support for critical migrations (if feasible)

## GitHub Actions CI/CD

| Step | Trigger |
|---|---|
| Syntax checks & linting | Every push / PR |
| Auto-formatting enforcement | Every push / PR |
| Unit tests (all 201+) | Every push / PR |
| Build `.AppImage` | Tagged release |
| Build `monitor.exe` | Tagged release (monitor repo) |
| Publish release + update `metadata.json` | Tagged release |

## Metadata File

Auto-generated `metadata.json` tracks:
- `version` — current launcher version
- `channel` — release channel (stable, beta)
- `upstream` — launcher GitHub repo
- `update_url` — URL to check for updates
- `migration_version` — latest applied migration
