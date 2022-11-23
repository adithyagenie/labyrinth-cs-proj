import curses

from maze.modules.maze import main


def bruh():
    curses.wrapper(main)
    curses.nocbreak()
    curses.echo()
    curses.endwin()
