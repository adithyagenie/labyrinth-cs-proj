#
# Copyright © 2023 adithyagenie
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#

import curses
import os
import pickle
from time import sleep

import maze.menu as m

from .PlayerBase_func import input, screenwipe


def save(screen, maze, coords, elapsed):
    """Saves the maze to a binary file"""
    y, x = screen.getmaxyx()
    if "saves" not in os.listdir():
        os.mkdir("saves")
    names = os.listdir("saves")
    screen.addstr(17, x - 17, "Enter filename: ")
    name = input(18, x - 17, screen)
    if names:
        for i in range(len(names)):
            names[i] = names[i].replace(".maze", "")
        for i in range(len(names)):
            for j in range(len(names) - i - 1):
                if int(names[j].split("_")[1]) > int(names[j + 1].split("_")[1]):
                    names[j], names[j + 1] = names[j + 1], names[j]
        num = int(names[-1].split("_")[1]) + 1
        if not name:
            name = "default"
        filename = f"maze_{str(num)}_{name}.maze"
    else:
        filename = f"maze_0_{name}.maze"
    f = open("saves//" + filename, "wb")
    pickle.dump(maze, f)
    pickle.dump(coords, f)
    pickle.dump(elapsed, f)
    f.close()
    screen.addstr(19, x - 17, "Maze saved!")
    screen.refresh()
    sleep(3)
    screen.addstr(17, x - 17, " " * 16)
    screen.addstr(18, x - 17, " " * 16)
    screen.addstr(19, x - 17, " " * 12)
    screen.refresh()


def check():
    if len(os.listdir("saves")):
        return True


def load(screen):
    """Loads a maze and returns maze, coords and time"""
    y, x = screen.getmaxyx()
    screen.clear()
    screen.refresh()
    screen.border()
    screen.addstr(2, x // 2 - 4, "LOAD MAZE", curses.color_pair(3) | curses.A_BOLD)
    mazes = os.listdir("saves")
    sy = 5
    for i in range(len(mazes)):
        msg = f"{str(i + 1)}. Maze {((mazes[i].replace('.maze', '')).split('_'))[1]} - {((mazes[i].replace('.maze', '')).split('_'))[2]}"
        screen.addstr(sy, x // 2 - len(msg) // 2, msg)
        sy += 1
    while True:
        screen.addstr(y // 2 + 5, x // 2 - 15, "Enter preferred maze number: ")
        num = input(y // 2 + 5, x // 2 + 14, screen)
        if num and type(int(num)) == type(0):
            num = int(num) - 1
        else:
            screen.clear()
            screen.refresh()
            m.menu(screen)
            return
        if num < len(mazes):
            break
        else:
            screen.addstr(
                y - 5,
                x // 2 - 23,
                "Entered maze doesn't exist. Please try again.",
                curses.color_pair(1),
            )
            while True:
                key = screen.getch()
                if key == 10:
                    screen.addstr(y - 1, 0, " " * (x - 5))
                    screenwipe(screen, 30, y // 2 + 5)
                    screen.refresh()
                    break
            continue
    f = open("saves//" + mazes[num], "rb")
    maze = pickle.load(f)
    coords = pickle.load(f)
    elapsed = pickle.load(f)
    f.close()
    return maze, coords, elapsed
