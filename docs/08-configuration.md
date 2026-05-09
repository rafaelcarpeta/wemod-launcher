# Configuration

Config lives in `$XDG_CONFIG_HOME/wand/`.

## Files

| File | Purpose |
|---|---|
| `config.json` | User configuration (merged with defaults) |
| `metadata.json` | Auto-generated: version, channel, upstream info, URLs, repos |

## Loading

1. Start with hardcoded defaults
2. Deep-merge with `config.json` from disk (if exists)
3. Apply env var overrides
4. Return merged result

## Config Sections

- **paths**: steam_compat, wine_prefix, scan_folders
- **upstream**: repo, prefix_repo
- **features**: troubleshooter, skip_exe_validation, pre_launch_command, early_exit_timeout
- **debug**: verbose, package_prefix

## Metadata

Auto-generated file tracking: current version, upstream repo, user agent for HTTP requests.

## Source Values File

A JSON file distributed with the launcher containing things that change often:
- Wand download URLs
- Monitor download URL
- Default user agent string
- Repo names for launcher and prefix downloads
- Prefix release tag pattern

This way URLs can be updated without a code release.

## Old Config Format (Legacy Reference)

The previous launcher used an INI-format config file (`wemod.conf`). The rewrite uses JSON in XDG paths, but these old settings show what existed before:

```ini
[Settings]
Version=1.535
ScriptName=wemod-launcher
WeModLog=wemod.log
VirtualEnvironment=wemod_venv
SteamCompatDataPath=           # → paths.steam_compat
WinePrefixPath=                # → paths.wine_prefix
ScanFolder=                    # → paths.scan_folders
RepoUser=DeckCheatz            # → upstream.repo (user/repo combined)
RepoName=BuiltPrefixes-dev     # → upstream.prefix_repo (user/repo combined)
Troubleshoot=true              # → features.troubleshooter
PackagePrefix=                 # → debug.package_prefix
SelfUpdate=                    # (evaluate: auto-update guard)
NoEXE=                         # → features.skip_exe_validation
```

Notable differences from the old format:
- `VirtualEnvironment` — no longer needed (we use system Python / venv managed by distro)
- `ScriptName` — deprecated
- `RepoUser` + `RepoName` → combined into `upstream.repo` as `user/repo` format
