CLI interface: structured arg parser, subcommands, and non-interactive mode

Proposed by: marvin1099 — docs/01-arg-parser.md, docs/12-cli-commands.md; github.com/DeckCheatz/wemod-launcher/discussions/258 (item 2)

Give the launcher a first-class CLI surface so it can be operated without
relying on environment variables and config files. A dedicated `ArgParser`
splits raw argv into well-defined fields (`wand_flags`, `dry_run`,
`cli_command`, `cli_subargs`, `game`, `game_args`, `game_tools`) by
scanning for a known separator (e.g. `--wand--`) for a clean split or
otherwise best-guessing by consuming known flags left-to-right with
explicit arity rules (0, 1, or variadic with boundary detection on
separators, known flags, Wine/Proton binaries, or Proton verbs). Game
detection runs internally using a multi-step strategy — URL, extension,
PE-header sniff, Proton verb, known-binary heuristic, positional,
last-resort — and ambiguous input raises `ArgParseError`. Disambiguation
between flags and CLI commands (e.g. `--prefix`) is done by peeking at the
next argument for a known subcommand.

A small set of `--`-prefixed CLI commands is dispatched after parsing:
`--help` and `--version` for basic info, `--config show|reset` to
inspect or restore config, `--prefix list|show <path>|clean` for prefix
DB inspection and cleanup, and `--cache clean` to wipe cached downloads.
Return codes are contractual — 0 for success, 1 for caught `WandError`s,
anything greater than 1 for unhandled exceptions — so scripts and CI can
reliably distinguish user-facing failures from real bugs.
