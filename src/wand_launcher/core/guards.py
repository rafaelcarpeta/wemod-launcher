#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

import os
import sys
from collections.abc import Callable
from typing import Any


def check_root(settings: Any, log: Any, interface: Any) -> None:
    if os.geteuid() != 0:
        return

    if getattr(settings, "is_force_root_active", False):
        return

    log.info("launcher.root_check", "Running as root — showing warning.")
    interface.show_message(
        "Running as root is not allowed.\n"
        "Use --force-root to override (not recommended)."
    )
    sys.exit(1)


def step(
    interface: Any, name: str, fn: Callable[..., Any], user_msg: str, *args: Any
) -> bool:
    try:
        fn(*args)
        return False
    except Exception:
        interface.error_msg_and_log(name, user_msg)
        return True


def step_code(
    interface: Any, name: str, fn: Callable[..., Any], user_msg: str, *args: Any
) -> tuple[bool, int]:
    try:
        result = fn(*args)
        return False, (result if result is not None else 0)
    except Exception:
        interface.error_msg_and_log(name, user_msg)
        return True, 1
