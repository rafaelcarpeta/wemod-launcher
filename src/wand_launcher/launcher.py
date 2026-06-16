#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

"""Main entry point — orchestrates the full launcher lifecycle."""

import sys
from typing import Any


def main() -> int:
    """Bootstrap → step flow → troubleshooter."""

    # ── Bootstrap ──────────────────────────────────────────────────

    from .core.paths import PathManager

    path_mgr = PathManager()

    from .logging.event_bus import LogManager

    log = LogManager(path_mgr)
    log.info("launcher.start", "Launcher started")

    from .core.args import ArgManager
    from .core.settings import SettingsManager

    args = ArgManager()
    settings = SettingsManager(args)

    from .ui.detect import detect_interface

    interface = detect_interface(settings, log)

    from .core.guards import check_root

    check_root(interface, settings)

    settings.load_config()

    # ── Step Flow / Troubleshooter ─────────────────────────────────

    exit_code = _run_flow(path_mgr, settings, interface, log)

    from .core.runner import StepRunner

    runner = StepRunner(interface, path_mgr, settings, log)
    from .troubleshooter import run_troubleshooter

    if runner.run(
        "troubleshooter", "Could not run the troubleshooter.", run_troubleshooter
    ):
        exit_code = 1

    return exit_code


def _run_flow(path_mgr: Any, settings: Any, interface: Any, log: Any) -> int:
    """Download app → prefix setup → sync data → monitor launch."""
    from .core.runner import StepRunner

    runner = StepRunner(interface, path_mgr, settings, log)

    from .updater import update_if_needed

    if runner.run("updater", "Could not check for updates.", update_if_needed, i=False):
        return 1

    from .migrations import apply_migrations

    if runner.run(
        "apply_migrations",
        "Failed to apply data migrations.",
        apply_migrations,
        p=False,
        i=False,
    ):
        return 1

    from .app_installer import ensure_app

    if runner.run("download_app", "Could not download the app.", ensure_app):
        return 1

    from .prefix_manager import setup_prefix

    if runner.run("prefix_setup", "Could not set up the Wine prefix.", setup_prefix):
        return 1

    from .data_sync import sync_app_data

    if runner.run("data_sync", "Could not sync app data.", sync_app_data, i=False):
        return 1

    from .monitor import launch_monitor

    _, code = runner.run_code(
        "monitor_launch", "Cannot launch the monitor.", launch_monitor
    )
    return code


if __name__ == "__main__":
    sys.exit(main())
