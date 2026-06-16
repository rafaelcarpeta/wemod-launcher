#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

from collections.abc import Callable
from typing import Any

from .guards import step, step_code


class StepRunner:
    def __init__(self, settings: Any, log: Any, interface: Any) -> None:
        self.settings = settings
        self.log = log
        self.interface = interface

    def run(
        self,
        name: str,
        user_msg: str,
        fn: Callable[..., Any],
    ) -> bool:
        return step(
            self.interface,
            f"launcher.flow.{name}",
            fn,
            user_msg,
            self.settings,
            self.log,
            self.interface,
        )

    def run_code(
        self,
        name: str,
        user_msg: str,
        fn: Callable[..., Any],
    ) -> tuple[bool, int]:
        return step_code(
            self.interface,
            f"launcher.flow.{name}",
            fn,
            user_msg,
            self.settings,
            self.log,
            self.interface,
        )
