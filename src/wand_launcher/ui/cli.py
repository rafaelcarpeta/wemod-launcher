#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

from typing import Any


class CLIInterface:
    def __init__(self, settings: Any, log: Any) -> None:
        self._settings = settings
        self._log = log

    def show_message(self, text: str) -> None:
        print(text)

    def error_msg_and_log(self, type_: str, text: str) -> None:
        self._log.error(type_, text)
        print(f"Error: {text}")
