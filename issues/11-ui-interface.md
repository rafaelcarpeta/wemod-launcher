Unified UI interface with CLI/GUI impls and --no-prompt auto-answer

Proposed by: marvin1099 — docs/13-ui-interface.md; github.com/DeckCheatz/wemod-launcher/discussions/258 (item 3)

Replace direct `print()`/`input()` in business logic with a single
abstract UI interface exposing `show_message`, `show_error`, `confirm`,
`choose`, `directory_picker`, and `progress` (returning a
`ProgressHandle` with `update`, `complete`, `fail`). The CLI
implementation routes messages/errors to stderr, uses stdin prompts and
numbered menus, and renders progress as an in-place spinner or
percentage line; the GUI implementation uses PyQt6 `QDialog`s only (no
persistent main window) and falls back to the CLI implementation when
PyQt6 isn't available. Progress in the GUI is a modal dialog with a
progress bar and status text; in indeterminate mode the fraction is
ignored and only status text updates are shown.

A `--no-prompt` mode auto-answers everything (confirm → True, choose →
first option, picker → default or empty, progress → silent) so the
launcher can run unattended without code paths branching on
interactivity. The result is a consistent user experience across modes
and removal of scattered tty-detection logic from feature code.
