#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

"""StepRunner — convenience wrapper around step() / step_code()."""

from collections.abc import Callable
from typing import Any

from .guards import step, step_code


class StepRunner:
    """Convenience wrapper that captures the four core objects.

    Builds *args from boolean flags so calls are concise::

        runner = StepRunner(interface, path_mgr, settings, log)

        # Pass path_mgr, settings, log — skip interface
        if runner.run("updater", "Could not check for updates.",
                       update_if_needed, i=False):
            return 1

        # Pass all four (default for every flag)
        _, code = runner.run_code("monitor_launch", "Cannot launch the monitor.",
                                   launch_monitor)
    """

    def __init__(self, interface: Any, path_mgr: Any, settings: Any, log: Any) -> None:
        self.interface = interface
        self.path_mgr = path_mgr
        self.settings = settings
        self.log = log

    def _build_args(self, p: bool, s: bool, i: bool, lg: bool) -> list[Any]:
        args: list[Any] = []
        if p:
            args.append(self.path_mgr)
        if s:
            args.append(self.settings)
        if i:
            args.append(self.interface)
        if lg:
            args.append(self.log)
        return args

    def run(
        self,
        name: str,
        user_msg: str,
        fn: Callable[..., Any],
        p: bool = True,
        s: bool = True,
        i: bool = True,
        lg: bool = True,
    ) -> bool:
        """Call step() with ``launcher.flow.{name}`` and the selected args."""
        return step(
            self.interface,
            f"launcher.flow.{name}",
            fn,
            user_msg,
            *self._build_args(p, s, i, lg),
        )

    def run_code(
        self,
        name: str,
        user_msg: str,
        fn: Callable[..., Any],
        p: bool = True,
        s: bool = True,
        i: bool = True,
        lg: bool = True,
    ) -> tuple[bool, int]:
        """Call step_code() with ``launcher.flow.{name}`` and the selected args."""
        return step_code(
            self.interface,
            f"launcher.flow.{name}",
            fn,
            user_msg,
            *self._build_args(p, s, i, lg),
        )
