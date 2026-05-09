# Monitor Process

The monitor is a **separate project** in its own repository. This section describes the contract between launcher and monitor.

## Purpose

- Runs inside the Wine prefix as a Windows PE
- Manages Wand.exe and game process lifecycle
- Communicates with launcher over TCP
- Uses a **config-driven** model: processes and their relationships are defined declaratively, not hardcoded

## Launch

The launcher starts the monitor as a subprocess with these CLI arguments:

```
monitor.exe --port <PORT> --error-file Z:\path\to\error.json --timeout 10
```

- `--port`: TCP port for IPC (launcher listens on a random port, passes it to monitor)
- `--error-file`: Z:-style path where the monitor writes a fallback error JSON if TCP connection fails
- `--timeout`: seconds the monitor waits before assuming the connection is dropped (default: 10)

The error file can be placed anywhere on the Linux filesystem via Z: drive (Wine maps Z: to `/`). This avoids restricting error output to `drive_c/` inside the prefix.

## Communication Protocol

- **Transport**: TCP on `127.0.0.1`
- **Format**: newline-delimited JSON
- **Direction**: launcher sends config, monitor sends events, launcher sends commands

### Launcher → Monitor

| Message | Payload | When |
|---|---|---|
| LaunchConfig | session_id, process list, lifecycle settings | After TCP connection |
| shutdown | (none) | After session complete |

### Monitor → Launcher

See [Event-Driven Model](#event-driven-model) for the full event list. All events are newline-delimited JSON over TCP.

## Config-Driven Process Definitions

Processes are defined declaratively — the monitor does not hardcode any process logic:

| Field | Type | Description |
|---|---|---|
| `name` | str | Process identifier (used in events) |
| `executable` | str | Path to the binary (Z:-style inside Wine) |
| `args` | list[str] | Command-line arguments |
| `working_dir` | str | Working directory (Z:-style) |
| `dependencies` | list[str] | Names of processes that must start before this one |
| `wait_for_exit` | bool | Whether the monitor waits for this process to exit before shutdown |

Startup order: resolved from `dependencies` — topological sort. If a dependency fails, dependent processes are not started.

Shutdown order: reverse of startup order. Configurable `shutdown_delay` between kills and `exit_timeout` before force-kill.

## Event-Driven Model

The monitor emits structured events for every lifecycle change — the launcher reacts, not polls:

| Event | Payload | Description |
|---|---|---|
| `process_started` | name, pid | A managed process started |
| `process_exited` | name, pid, exit_code | A managed process exited |
| `process_crashed` | name, pid, exit_code, reason | A managed process crashed (non-zero + unexpected) |
| `session_complete` | exit_code, summary | Game session ended |
| `stdout` | name, line | Newest stdout line from a process |
| `warning` | message | Non-fatal issue |
| `error` | message | An error occurred (may be a connection error; if so, write to error.json — see Error Fallback) |

### LaunchConfig Structure

See [Config-Driven Process Definitions](#config-driven-process-definitions) for the process definition schema. LaunchConfig wraps an array of those plus lifecycle settings (shutdown delay, exit timeout).

### Process Ordering

1. Start Wand.exe first
2. After Wand signals ready, start the game
3. Wand is a dependency of game (resolved from the process definitions)

## Error Fallback

If the monitor cannot establish TCP (e.g. launcher crashed), it writes an error JSON file to the path specified by `--error-file` before exiting. The launcher polls this file while waiting for the TCP connection.

## Wine Environment

Monitor receives `WINEPREFIX` env var and Z:-style paths from the launcher.
