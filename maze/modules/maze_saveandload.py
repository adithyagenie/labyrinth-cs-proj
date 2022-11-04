import os
import pickle
from time import sleep

import maze.modules.maze as m

from .PlayerBase_func import Input, screenwipe


def save(screen, maze, coords):
    y, x = screen.getmaxyx()
    if "saves" not in os.listdir():
        os.mkdir("saves")
    names = os.listdir("saves")
    screen.addstr(17, x - 17, "Enter filename: ")
    name = Input(18, x - 17, screen)
    if names:
        num = int(((names[-1].replace(".maze", "")).split("_"))[1]) + 1
        if not name:
            name = "default"
        filename = f"maze_{str(num)}_{name}.maze"
    else:
        filename = f"maze_0_{name}.maze"
    f = open("saves//" + filename, "wb")
    pickle.dump(maze, f)
    pickle.dump(coords, f)
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
    y, x = screen.getmaxyx()
    screen.clear()
    screen.refresh()
    screen.addstr(2, x // 2 - 4, "LOAD MAZE")
    mazes = os.listdir("saves")
    sy = 4
    for i in range(len(mazes)):
        screen.addstr(
            sy,
            10,
            f"{str(i + 1)}. Maze {((mazes[i].replace('.maze', '')).split('_'))[1]} - {((mazes[i].replace('.maze', '')).split('_'))[2]}",
        )
        sy += 1
    while True:
        screen.addstr(y // 2 + 5, 0, "Enter preferred maze number: ")
        num = Input(y // 2 + 5, 30, screen)
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
            screen.addstr(y - 1, 0, "Entered maze doesn't exist. Please try again.")
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
    f.close()
    return maze, coords
