# Prefix Management

Track Wine prefixes and associate them with games.

## Database

Each prefix record has:
- Path on disk (this is also the id)
- wand installed tag
- Last validated timestamp
- Created / updated timestamps

## Operations

- **Scan**: detect prefix on disk, find game executables inside `drive_c/`, update DB
- **Validate**: check all tracked prefixes still exist on disk, mark missing
- **Clean**: remove missing entries from DB
- **Show**: get full record for a prefix path
- **List**: list all tracked prefixes with status
- **Normilize**: ensure prefix structure is consistent:
  - `pfx` should always be a symlink to `.` (so Wine/Proton sees a consistent layout)
  - `drive_c/users/<steamuser>` should be a symlink to the current Linux user (so login/wallet data is shared across prefixes)

## Sources

Prefixes can come from:
- **Download**: pre-built prefixes downloaded from a release repo
- **Build**: install to an existing Wine prefix (no new prefix created)
- **Steam**: detected via `STEAM_COMPAT_DATA_PATH` / `WINEPREFIX` environment
- **Manual**: user-specified via `--prefix`

## Game-Prefix Association

Track which game executable was last launched with which prefix. On subsequent launches of the same game, auto-resolve the prefix if none is specified.
