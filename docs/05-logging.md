# Logging

All logging goes through an event bus — never raw `print()` in business logic.

## EventBus

- Emit events by type with arbitrary data payload
- Subscribe handlers to specific event types or patterns
- Singleton accessible via `get_bus()`

## Log Levels

- `DEBUG` (10) — detailed debug info
- `INFO` (20) — normal operational info
- `WARN` (30) — warnings, non-fatal
- `ERROR` (40) — error conditions

## Handlers

| Handler | Output | Configurable |
|---|---|---|
| FileHandler | Session log file | path, level filter |
| ConsoleHandler | stderr | level set, topic patterns |
| CrashReporter | In-memory ring buffer | capacity |

## Level Configuration

Support three modes:
- **Threshold**: single level name → that level and above
- **Range**: `debug..warn` → inclusive range, open-ended with `debug..` or `..error`, bare `..` = all
- **Explicit set**: `debug,error` → only those levels (by name or number)

## Per-Stream Subscriptions

Components can subscribe to raw output streams of managed processes:

| Subscription | Payload | Description |
|---|---|---|
| `process.<name>.stdout` | line | New stdout line from a named process |
| `process.<name>.stderr` | line | New stderr line from a named process |

Enabled via config or `--log-topic` — only active when needed, no overhead otherwise.

## Structured Context

All events carry a structured payload (not just a string message):

| Field | Type | Description |
|---|---|---|
| `event` | str | Event name (e.g. `launch.start`) |
| `message` | str | Human-readable description |
| `data` | dict | Arbitrary structured data (process name, exit code, arguments, etc.) |
| `timestamp` | float | Unix timestamp |
| `source` | str | Component that emitted the event (e.g. `arg_parser`, `launch_manager`) |

## Topic Filtering

fnmatch-based glob patterns:
- `parser.*` → all parser events
- `parser.*,network.*` → parser AND network events (OR'd)

## Naming Convention

`<domain>.<action>` — e.g. `parser.start`, `parser.flag`, `launch.start`, `monitor.connected`, `cli.command`

Errors: `<domain>.error` — e.g. `cli.unknown_command`, `launch.no_prefix`
