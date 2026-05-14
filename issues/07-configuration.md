JSON configuration in $XDG_CONFIG_HOME/wand/ with deep-merged defaults

Proposed by: marvin1099 — docs/08-configuration.md

Move from the legacy INI `wemod.conf` to a JSON `config.json` under
`$XDG_CONFIG_HOME/wand/`, loaded by starting from hardcoded defaults,
deep-merging the on-disk file, and finally applying env-var overrides.
Config is partitioned into `paths` (steam_compat, wine_prefix,
scan_folders), `upstream` (repo, prefix_repo), `features`
(troubleshooter, skip_exe_validation, pre_launch_command,
early_exit_timeout), and `debug` (verbose, package_prefix) sections, with
auto-generated `metadata.json` tracking the current version, upstream
repo, and user-agent string for HTTP requests. A separate
`source_values.json` distributed with the launcher holds frequently-
changing values (Wand/monitor download URLs, repo names, prefix release
tag patterns) so they can be revised without a code release. Legacy
fields like `VirtualEnvironment` and `ScriptName` are dropped, and
`RepoUser`+`RepoName` collapse into a single `upstream.repo` in
`user/repo` form.
