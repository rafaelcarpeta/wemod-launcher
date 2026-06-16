#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

"""Interface detection — returns CLI or GUI interface."""

from typing import Any


def detect_interface(settings: Any, log: Any) -> Any:
    if settings.is_cli or settings.is_no_prompt:
        from .cli import CLIInterface

        return CLIInterface(settings, log)
    from .gui import GUIInterface

    return GUIInterface(settings, log)
