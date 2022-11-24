import curses
import sys
import time

import maze.modules.maze as m1
import maze.modules.maze_saveandload as sl
import maze.modules.PlayerBase_func as database
import pong
import snake
from maze.modules.about import about


def menu(screen):
    exit = False
    y, x = screen.getmaxyx()
    screen.clear()
    screen.nodelay(True)
    screen.refresh()
    text = """
    \t\t\t██       █████  ██████  ██    ██ ██████  ██ ███    ██ ████████ ██   ██
    \t\t\t██      ██   ██ ██   ██  ██  ██  ██   ██ ██ ████   ██    ██    ██   ██
    \t\t\t██      ███████ ██████    ████   ██████  ██ ██ ██  ██    ██    ███████
    \t\t\t██      ██   ██ ██   ██    ██    ██   ██ ██ ██  ██ ██    ██    ██   ██
    \t\t\t███████ ██   ██ ██████     ██    ██   ██ ██ ██   ████    ██    ██   ██"""

    screen.addstr(1, 5, str(text))
    screen.addstr(10, x // 2 - 2, "MENU")
    screen.addstr(13, 1, "space - Play")
    screen.addstr(14, 1, "f - Load game from file")
    screen.addstr(15, 1, "a - Account Settings")
    screen.addstr(16, 1, "l - Leaderboard")
    screen.addstr(17, 1, "x - About")
    screen.addstr(18, 1, "esc - Quit")
    screen.border()
    while True:
        if exit:
            break
        key = screen.getch()
        if key == ord(" "):
            screen.clear()
            screen.refresh()
            screen.border()
            screen.addstr(1, x // 2 - 2, "PLAY")
            screen.addstr(y // 2 - 4, x // 2 - 2, "1. MAZE")
            screen.addstr(y // 2 - 2, x // 2 - 2, "2. PONG")
            screen.addstr(y // 2, x // 2 - 2, "3. SNAKE")
            screen.addstr(y // 2 + 2, x // 2 - 2, "4. WORDLE")
            while True:
                key2 = screen.getch()
                if key2 == ord("1"):
                    m1.play(screen)
                elif key2 == ord("2"):
                    pong.main(screen)
                elif key2 == ord("3"):
                    snake.main(screen)
                elif key2 == ord("4"):
                    pass
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
                    time.sleep(1)
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
