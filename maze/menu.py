import curses
import sys
import time

import maze.modules.maze as m1
import maze.modules.maze_saveandload as sl
import maze.modules.PlayerBase_func as database
import pong
import snake
import wordle.wordle as wordlegame
from maze.modules.about import about


def menu(screen):
    """The Main menu of the entire game"""
    exit = False
    y, x = screen.getmaxyx()
    screen.clear()
    screen.nodelay(True)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    screen.refresh()
    text = """
    \t\t\t██       █████  ██████  ██    ██ ██████  ██ ███    ██ ████████ ██   ██
    \t\t\t██      ██   ██ ██   ██  ██  ██  ██   ██ ██ ████   ██    ██    ██   ██
    \t\t\t██      ███████ ██████    ████   ██████  ██ ██ ██  ██    ██    ███████
    \t\t\t██      ██   ██ ██   ██    ██    ██   ██ ██ ██  ██ ██    ██    ██   ██
    \t\t\t███████ ██   ██ ██████     ██    ██   ██ ██ ██   ████    ██    ██   ██"""

    screen.addstr(1, x // 2 - 34, str(text), curses.color_pair(5))
    screen.addstr(10, x // 2 - 2, "MENU", curses.color_pair(3) | curses.A_BOLD)
    screen.addstr(13, x // 2 - 6, "space - PLAY", curses.A_BOLD)
    screen.addstr(15, x // 2 - 11, "f - LOAD GAME FROM FILE", curses.A_BOLD)
    screen.addstr(17, x // 2 - 10, "a - ACCOUNT SETTINGS", curses.A_BOLD)
    screen.addstr(19, x // 2 - 7, "l - LEADERBOARD", curses.A_BOLD)
    screen.addstr(21, x // 2 - 4, "x - ABOUT", curses.A_BOLD)
    screen.addstr(23, x // 2 - 4, "esc - QUIT", curses.A_BOLD)
    screen.border()
    while True:
        if exit:
            break
        key = screen.getch()
        if key == ord(" "):
            screen.clear()
            screen.refresh()
            screen.border()
            screen.addstr(1, x // 2 - 2, "PLAY", curses.color_pair(3) | curses.A_BOLD)
            screen.addstr(y // 2 - 4, x // 2 - 2, "1. MAZE", curses.A_BOLD)
            screen.addstr(y // 2 - 2, x // 2 - 2, "2. PONG", curses.A_BOLD)
            screen.addstr(y // 2, x // 2 - 2, "3. SNAKE", curses.A_BOLD)
            screen.addstr(y // 2 + 2, x // 2 - 2, "4. WORDLE", curses.A_BOLD)
            while True:
                key2 = screen.getch()
                if key2 == ord("1"):
                    m1.play(screen)
                elif key2 == ord("2"):
                    pong.main(screen)
                elif key2 == ord("3"):
                    snake.main(screen)
                elif key2 == ord("4"):
                    screen.nodelay(False)
                    screen.keypad(False)
                    wordlegame.main(screen)
                elif key2 == 27:
                    menu(screen)
                    break
        elif key == 27:
            screen.clear()
            screen.refresh()
            screen.border()
            screen.addstr(y // 2 - 5, x // 2 - 5, "THANK YOU!")
            while True:
                breakkey = screen.getch()
                if breakkey:
                    time.sleep(2)
                    sys.exit()
        elif key == ord("a"):
            database.screenhandler(screen)
        elif key == ord("l"):
            database.leaderboard(screen)
        elif key == ord("x"):
            about(screen)
        elif key == ord("f"):
            present = sl.check()
            if present:
                maze = sl.load(screen)
                if maze:
                    m1.play(screen, maze[0], maze[1], maze[2])
                    return
                else:
                    screen.addstr(
                        20, 5, "No saved mazes present. Press enter to continue..."
                    )
                    while True:
                        key2 = screen.getch()
                        if key2 == 10:
                            screen.addstr(20, 5, " " * (x - 10))
                            break
