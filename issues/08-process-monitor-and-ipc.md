Config-driven Process Monitor with event-driven structured JSON IPC

Proposed by: marvin1099 — docs/09-monitor-contract.md; github.com/DeckCheatz/wemod-launcher/discussions/258 (items 6, 7, 8)

The Process Monitor lives in its own repo and runs inside the Wine prefix
as a Windows PE that manages Wand.exe plus the game lifecycle. The
launcher invokes it as
`monitor.exe --port <PORT> --error-file Z:\... --timeout 10` and they
speak newline-delimited JSON over local TCP on `127.0.0.1`. Launcher
sends `LaunchConfig` (declarative process definitions plus lifecycle
settings) and `shutdown`; monitor emits `process_started`,
`process_exited`, `process_crashed`, `session_complete`, `stdout`,
`warning`, and `error` events. If TCP can't be established, the monitor
writes a fallback JSON to the `--error-file` Z: path before exiting,
which the launcher polls — so even monitor-side failures produce
machine-parseable output instead of opaque log scrapes.

Process definitions are fully declarative — `name`, `executable`,
`args`, `working_dir`, `dependencies`, `wait_for_exit` — so startup
order is a topological sort over `dependencies` (Wand.exe before the
game) and failed dependencies short-circuit dependents. Shutdown
reverses the start order with configurable delay and force-kill timeout.
The launcher only ships the `LaunchConfig` and reacts to events rather
than polling status, so process lifecycle logic is unified, testable,
and easy to extend (extra helpers, side processes) without touching
launcher internals. The same event-driven model unifies inter-process
coordination across the whole stack.
