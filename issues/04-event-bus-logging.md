Event-bus logging with structured payloads, subscriptions, and topic filters

Proposed by: marvin1099 — docs/05-logging.md; github.com/DeckCheatz/wemod-launcher/discussions/258 (item 11)

Replace raw `print()` calls with an `EventBus` singleton that components
emit typed events on and that handlers (file, console, crash-reporter
ring buffer, custom listeners) subscribe to. Each event carries a
structured payload — `event`, `message`, `data`, `timestamp`, `source` —
using a `<domain>.<action>` naming convention (e.g. `parser.flag`,
`launch.start`, `cli.unknown_command`) so filtering and crash diagnostics
are precise. Level configuration supports threshold, range (`debug..warn`,
open-ended with `debug..` or `..error`, bare `..` = all), and explicit-set
modes, while fnmatch-style topic filters (`parser.*,network.*`) let users
and developers narrow output without grep-ing free-form log lines.

Per-stream subscriptions (`process.<name>.stdout`,
`process.<name>.stderr`) make it possible to tap into managed-process
output on demand without paying overhead by default, enabled via config or
`--log-topic`. The same subscription model replaces the current static
log-file approach and lets components emit structured events that
downstream tooling (troubleshooter, UI, future telemetry) can react to in
real time.
