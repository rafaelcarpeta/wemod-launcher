# CLI Commands

All CLI commands use a `--` prefix and are dispatched by the CLI handler after arg parsing.

## --help

Print usage information listing all available flags, CLI commands, and their arguments.

```
wand-launcher --help
```

## --version

Print the launcher version and exit.

```
wand-launcher --version
```

## --config

```
wand-launcher --config show      # print merged config as JSON (possible)
wand-launcher --config reset     # reset to defaults (possible)
```

## --prefix

```
wand-launcher --prefix list           # list all tracked prefixes  (possible)
wand-launcher --prefix show <path>    # show prefix record as JSON  (possible)
wand-launcher --prefix clean          # remove missing entries  (possible)
```

## --cache

```
wand-launcher --cache clean           # delete all cached files  (possible)
```

## Return Codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Caught WandError (user-facing error) |
| >1 | Unhandled exception (bug) |
 
Not shure about that one ^
