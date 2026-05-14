Typed WandError hierarchy with recoverability and crash reports

Proposed by: marvin1099 — docs/04-error-handling.md

All user-facing errors inherit from a base `WandError` class with specific
subclasses (`ArgParseError`, `ConfigError`, `DatabaseError`, `NetworkError`,
`PrefixError`, `IpcError`, `MigrationError`) so the engine can distinguish
expected failures from real bugs. Every error carries `message`,
`recoverable`, and `suggestion` fields, and the top-level engine catches
`WandError`, emits it to the event bus, dumps a crash report to the session
dir, and returns exit code 1, while non-`WandError` exceptions propagate
to the default excepthook. Crash reports bundle the recent log-event ring
buffer, the error message, and a timestamp so users and developers have
enough context to diagnose without re-running.
