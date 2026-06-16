#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

import json
import os
import sys


class SettingsManager:
    # NOTE: Not a real implementation. Arg parsing will be done in a separate
    # module, path generation will be done in a separate module.

    def __init__(self):
        raw = sys.argv[1:]

        self.is_force_root_active = "--force-root" in raw
        self.is_cli = "--cli" in raw
        self.is_no_prompt = "--no-prompt" in raw
        self.has_post_update = "--post-update" in raw
        self._positional = [a for a in raw if not a.startswith("--")]

        xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        xdg_cache = os.environ.get("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))

        self.data_dir = os.path.join(xdg_data, "wand")
        self.config_dir = os.path.join(xdg_config, "wand")
        self.cache_dir = os.path.join(xdg_cache, "wand")

        self.log_path = os.path.join(self.cache_dir, "launcher.log")
        self.metadata_path = os.path.join(self.data_dir, "metadata.json")
        self.bin_dir = os.path.join(self.data_dir, "bin")
        self.login_dir = os.path.join(self.data_dir, "login")
        self.prefixes_db_path = os.path.join(self.data_dir, "prefixes.json")

        self._config = {}
        self._games_config = {}
        self._metadata = {}

    def load_all(self):
        config_path = os.path.join(self.config_dir, "config.json")
        if os.path.isfile(config_path):
            with open(config_path) as f:
                self._config = json.load(f)

        games_path = os.path.join(self.config_dir, "games.json")
        if os.path.isfile(games_path):
            with open(games_path) as f:
                self._games_config = json.load(f)

        if os.path.isfile(self.metadata_path):
            with open(self.metadata_path) as f:
                self._metadata = json.load(f)

    @property
    def positional_args(self):
        return list(self._positional)
