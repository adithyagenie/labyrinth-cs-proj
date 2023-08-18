#
# Copyright © 2023 adithyagenie
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#

import curses
import sys

from maze.modules.maze import main


def bruh():
    """Initialising the screen"""
    try:
        curses.wrapper(main)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    except KeyboardInterrupt:
        print("\n\n\nTerminating...")
        sys.exit()
