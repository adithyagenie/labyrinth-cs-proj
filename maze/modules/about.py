#
# Copyright © 2023 adithyagenie
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#

import curses

import maze.menu


def about(screen):
    """Displays the about screen"""
    y, x = screen.getmaxyx()
    screen.clear()
    screen.refresh()
    screen.border()
    screen.addstr(1, x // 2 - 2, "ABOUT US", curses.color_pair(3) | curses.A_BOLD)
    screen.addstr(
        3,
        5,
        "This game which you have played was developed as a high-school CS project.",
    )
    screen.addstr(
        5,
        5,
        "There are a series of retro games namely the maze, pong, snake and wordle.",
    )
    screen.addstr(
        6,
        5,
        "The maze is generated which always has a path towards the right bottom corner by using ",
    )
    screen.addstr(7, 5, "a famous generation algorithm named Depth First Search (DFS).")
    screen.addstr(
        9,
        5,
        "This game makes use of the 'curses' module which runs on any operating system in the native terminal.",
    )
    screen.addstr(
        10,
        5,
        "It makes use of SQL tables to store login details and maintain a leaderboard.",
    )
    screen.addstr(
        11,
        5,
        "It also makes use of binary files to save and load mazes and other credentials necessary.",
    )
    screen.addstr(15, 5, "This project has been an absolute blast to make.")
    screen.addstr(
        16, 5, "We thank you for playing this! Hope you liked it as much as we did!"
    )
    screen.addstr(21, 5, "Signing off,")
    screen.addstr(22, 5, "The Labyrinth")
    screen.addstr(y - 2, x - 31, "Press Esc to exit this screen.")
    screen.refresh()
    while True:
        key = screen.getch()
        if key == 27:
            break
    maze.menu.menu(screen)
    return
