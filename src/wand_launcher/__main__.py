#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only

"""Entry point for ``python -m wand_launcher`` — delegates to launcher.main()."""

import sys

from .launcher import main

if __name__ == "__main__":
    sys.exit(main())
