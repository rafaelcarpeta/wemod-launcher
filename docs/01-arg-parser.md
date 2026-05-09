# ArgParser

Responsible for splitting raw CLI arguments into structured fields. Game detection is handled internally — not a separate public component.

## Public API

```python
parsed = ArgParser(sys.argv[1:])
# Fields:
parsed.wand_flags      # dict of launcher flags
parsed.dry_run         # bool (popped from flags)
parsed.cli_command     # str or None ("config", "prefix", …)
parsed.cli_subargs     # list of args after CLI command
parsed.game            # str or None (executable path or URL)
parsed.game_args       # list of args after the game
parsed.game_tools      # list of tools before the game (proton, reaper, …)
```

## Internal Steps

### 1. Separator Scan

Search for a known separator (e.g. `--wand--`) anywhere in args.
- **Found** → split definitively: left = launcher flags, right = game chain
- **Not found** → best-guess: extract known flags left-to-right

### 2. Flag Extraction

Scan left-to-right, consuming known flags. Stop at anything unrecognized.

**Flag arity types:**
- **0** — boolean flag (no value), e.g. `--dry-run`
- **1** — flag takes one value, e.g. `--prefix /path`
- **-1** — variadic: consumes everything until a boundary

**Variadic boundary detection:**
A variadic flag (e.g. `--wand-args`) consumes following args until:
- A separator
- Another known flag
- A known Wine/Proton binary name
- A Proton verb (`run`, `waitforexitandrun`)

After variadic stops at a boundary:
- If boundary is a boolean (arity-0) flag → continue extraction (it's self-contained)
- Otherwise → stop extraction entirely

**CLI disambiguation:**
When a flag name is also a CLI command (e.g. `--prefix`), check if the next arg is a known subcommand (`list`, `show`, `clean`). If so, treat as CLI command, not flag.

### 3. CLI Command Detection

If no separator was found and the remaining chain starts with a known CLI command:
- Strip the `--` prefix
- Store the rest as subargs
- Clear the chain (no game launch)

**Supported CLI commands:**
- `--version` — print version
- `--help` — print usage
- `--config show|reset` (possibility)
- `--prefix list|show <path>|clean` (possibility)
- `--cache clean` (possibility)

### 4. Game Detection (internal, part of argparing) 

Scans the remaining chain for the game executable or URL using multi-step detection:

1. **URL** — contains `://` (e.g. `origin://game/12345`)
2. **Extension** — ends with `.exe` or `.url`
3. **PE header** — file starts with `MZ` bytes (Windows PE, even without `.exe`) (possibility)
4. **Proton verb** — arg after `run` / `waitforexitandrun` (possibility)
5. **Known binary** — arg after a known binary (wine, proton, umu-run…) if the next arg looks game-like (possibility)
6. **Positional** — first non-flag arg whose basename isn't a known binary (possibility, may error instead)
7. **Last resort** — the very first argument (possibility, may error instead)

Returns `(index, executable, remaining_args)` — stored in `game`, `game_args`, `game_tools`.

### 5. Validation

If a variadic flag consumed all remaining args with no separator and no game/CLI target → raise error (ambiguous input).

## Examples

```
# Steam: separator present, clear split
wand-launcher --wand-- reaper proton run game.exe +arg1

# Lutris: no separator, flags extracted, chain intact
wand-launcher --log-level=debug --no-prompt gamemoderun proton run game.exe

# Variadic wand-args with boundary
wand-launcher --wand-args foo bar --dry-run game.exe
# → wand_args=[foo, bar], dry_run=true, game=game.exe

# CLI command
wand-launcher --config show
# → cli_command=config, cli_subargs=[show]

# Help
wand-launcher --help
# → print usage and exit
```
