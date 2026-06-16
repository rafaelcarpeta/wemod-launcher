#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

import sys
from typing import Any


def main() -> int:
    from .core.settings import SettingsManager

    settings = SettingsManager()

    from .logging.event_bus import LogManager

    log = LogManager(settings)
    log.info("launcher.start", "Launcher started")

    from .ui.detect import detect_interface

    interface = detect_interface(settings, log)

    from .core.guards import check_root

    check_root(settings, log, interface)

    settings.load_all()

    exit_code = _run_flow(settings, log, interface)

    from .core.runner import StepRunner

    runner = StepRunner(settings, log, interface)
    from .troubleshooter import run_troubleshooter

    if runner.run(
        "troubleshooter", "Could not run the troubleshooter.", run_troubleshooter
    ):
        exit_code = 1

    return exit_code


def _run_flow(settings: Any, log: Any, interface: Any) -> int:
    from .core.runner import StepRunner

    runner = StepRunner(settings, log, interface)

    from .updater import update_if_needed

    if runner.run("updater", "Could not check for updates.", update_if_needed):
        return 1

    from .migrations import apply_migrations

    if runner.run(
        "apply_migrations",
        "Failed to apply data migrations.",
        apply_migrations,
    ):
        return 1

    from .app_installer import ensure_app

    if runner.run("download_app", "Could not download the app.", ensure_app):
        return 1

    from .prefix_manager import setup_prefix

    if runner.run("prefix_setup", "Could not set up the Wine prefix.", setup_prefix):
        return 1

    from .data_sync import sync_app_data

    if runner.run("data_sync", "Could not sync app data.", sync_app_data):
        return 1

    from .monitor import launch_monitor

    _, code = runner.run_code(
        "monitor_launch", "Cannot launch the monitor.", launch_monitor
    )
    return code


if __name__ == "__main__":
    sys.exit(main())
