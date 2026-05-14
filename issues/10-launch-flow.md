Structured launch flow with explicit dry-run, CLI, and launch states

Proposed by: marvin1099 — docs/11-launch-flow.md

Model the launcher's top-level behavior as three explicit states —
dry-run, CLI command, and launch — each with a documented step sequence
and exit contract. Dry-run parses args, loads config, validates prefixes,
prints a summary, and exits 0. CLI command parses args, detects the
command, dispatches to a handler (config/prefix/cache/version), prints
the result, and exits 0 or 1.

The launch path is fully ordered: parse args, resolve prefix via
SettingsManager, scan and validate the prefix DB, install or sync
Wand.exe, start a TCP IPC server on a random port, locate the monitor
binary, build the monitor command for the appropriate scenario (Steam
tool chain, standalone Windows PE under wine, or bare binary), and spawn
it with `WINEPREFIX`. The launcher then writes an error fallback (status
pending), sends `LaunchConfig` over IPC, waits for connection and
`session_complete` with timeouts, runs the troubleshooter on timeout or
non-zero exit, sends shutdown, waits for the monitor to exit (killing if
needed), and returns the exit code — every step is an event-emitting
checkpoint rather than an implicit side-effect.
