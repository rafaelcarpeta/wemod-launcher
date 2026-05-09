# Error Handling

All user-facing errors inherit from a base error class.

## Hierarchy

```
WandError
  ├── ArgParseError      — ambiguous/invalid arguments
  ├── ConfigError        — config file issues, missing prefix
  ├── DatabaseError      — prefix DB read/write failures
  ├── NetworkError       — download failures, checksum mismatch
  ├── PrefixError        — prefix creation/initialization failures
  ├── IpcError           — monitor TCP communication failures
  └── MigrationError     — config/DB migration failures
```

## Base Error Fields

| Field | Type | Purpose |
|---|---|---|
| `message` | str | Human-readable description |
| `recoverable` | bool | Can the user fix and retry? |
| `suggestion` | str | Suggested action for the user |

## Catch Pattern

The engine catches `WandError` at the top level:
1. Emit to event bus (with message, recoverable, suggestion)
2. Dump crash report to session dir
3. Return exit code 1

Non-WandError exceptions (actual bugs) propagate to the default excepthook.

## Crash Reports

Dumped to session directory on any error. Contains:
- Recent log events (ring buffer)
- Error message
- Timestamp

## Defining New Errors

```python
class MySpecificError(WandError):
    """Description of when this applies."""
    pass

raise MySpecificError(
    "Something went wrong.",
    recoverable=True,
    suggestion="Try running with --no-prompt"
)
```
