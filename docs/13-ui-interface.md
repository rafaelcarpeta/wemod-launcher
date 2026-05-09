# UI Interface

All user interaction goes through an abstract interface — never direct `print()`/`input()` in business logic.

## Methods

- `show_message(text)` — informational message
- `show_error(text)` — error message
- `confirm(text)` → bool — yes/no confirmation
- `choose(text, options)` → str or None — pick from a list
- `directory_picker(text, default)` → str or None — pick a directory
- `progress(label, indeterminate=False)` → ProgressHandle — start a progress indicator

### ProgressHandle

Returned by `progress()`, used to report progress during long operations (downloads, scanning, etc.):

| Method | Description |
|---|---|
| `.update(progress=0.0, status="")` | Set progress fraction (0.0–1.0) and optional status text |
| `.complete(status="")` | Mark as done |
| `.fail(status="")` | Mark as failed |

In indeterminate mode, the fraction is ignored — only status text updates are shown.

## Implementations

### CLI
- Messages/errors → stderr
- Confirm → stdin prompt
- Choose → numbered menu
- Directory pick → manual path input
- Progress → spinner or percentage line (updated in place)

### GUI
- PyQt6 QDialogs only — no persistent main window
- Falls back to CLI if PyQt6 unavailable
- Progress → modal dialog with progress bar and status text

## --no-prompt Mode

When set, all prompts auto-answer:
- confirm → True
- choose → first option
- directory_picker → default or empty
- progress → runs silently (no visual feedback)
