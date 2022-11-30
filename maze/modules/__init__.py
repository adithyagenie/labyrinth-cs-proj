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
