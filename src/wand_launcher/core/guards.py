#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

"""Root guard and step guard — protective wrappers for the launcher."""

import os
import sys
from collections.abc import Callable
from typing import Any


def check_root(interface: Any, settings: Any) -> None:
    """Exit with a message if running as root without --force-root.

    Called early in bootstrap, before any config files are loaded.
    Uses the interface so the message is visible in GUI or CLI mode.
    """
    if os.geteuid() != 0:
        return

    if getattr(settings, "is_force_root_active", False):
        return

    interface.show_message(
        "Running as root is not allowed.\n"
        "Use --force-root to override (not recommended)."
    )
    sys.exit(1)


def step(
    interface: Any, name: str, fn: Callable[..., Any], user_msg: str, *args: Any
) -> bool:
    """Run a flow step, notify on failure.

    Returns True if the step failed, False on success.
    Short form for intermediate steps — no return value needed.
    """
    try:
        fn(*args)
        return False
    except Exception:
        interface.error_msg_and_log(name, user_msg)
        return True


def step_code(
    interface: Any, name: str, fn: Callable[..., Any], user_msg: str, *args: Any
) -> tuple[bool, int]:
    """Run a flow step, notify on failure.

    Returns (failed, code). Used when the exit code matters
    (e.g. launch_monitor). On success *code* is the fn's result
    (or 0 if None); on exception *code* is 1.
    """
    try:
        result = fn(*args)
        return False, (result if result is not None else 0)
    except Exception:
        interface.error_msg_and_log(name, user_msg)
        return True, 1
