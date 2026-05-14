Restructure codebase by functional responsibility, not arbitrary groups

Proposed by: marvin1099 — github.com/DeckCheatz/wemod-launcher/discussions/258 (item 1)

Reorganize the source tree so files are grouped by what they actually do
— e.g. `wine_tools`, `path_utils`, `prefix_manager`, `arg_parser`,
`settings_manager`, `ui` — rather than by the ad-hoc layout inherited
from the original launcher. The current grouping mixes unrelated
concerns into shared modules, which makes the code harder to read,
harder to test in isolation, and harder for new contributors to locate
behaviour. A responsibility-based layout maps directly onto the
architecture documents (arg parser, settings manager, monitor contract,
path utilities, etc.), so each rewrite component lands in a
discoverable place and cross-cutting concerns stay confined to small,
single-purpose modules.
