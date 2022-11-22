import curses
import random
import sys
import time
from collections import defaultdict
from itertools import tee
from math import cos, exp, fabs, pi

import maze.modules.maze_saveandload as sl
import maze.modules.PlayerBase_func as database

from .about import about

WON = 0
PAUSED = False
CONNECTED = {"N": 1, "S": 2, "E": 4, "W": 8}
DIRECTIONS = {"N": (-1, 0), "S": (1, 0), "E": (0, 1), "W": (0, -1)}
ANTIPODES = {"N": "S", "S": "N", "W": "E", "E": "W"}

WALL = {
    12: "═",
    3: "║",
    10: "╗",
    5: "╚",
    9: "╝",
    6: "╔",
    7: "╠",
    11: "╣",
    14: "╦",
    13: "╩",
    15: "╬",
    0: " ",
    4: "═",
    8: "═",
    1: "║",
    2: "║",
}

VISITED = 16


class Maze:
    def __init__(self, height, width, start=(0, 0)):
        self.height = height
        self.width = width - 11
        self.stack = []
        self.cells = {(y, x): 0 for y in range(self.height) for x in range(self.width)}
        self.build(start)

    def eligible_neighbours(self, y, x):
        return [
            ((y + i, x + j), d)
            for d, (i, j) in DIRECTIONS.items()
            if (y + i, x + j) in self.cells.keys()
            and not self.cells[(y + i, x + j)] & VISITED
        ]

    def connected_cells(self, y, x):
        cell_directions = [d for (d, v) in CONNECTED.items() if v & self.cells[(y, x)]]
        return {
            (y + i, x + j): d
            for d, (i, j) in DIRECTIONS.items()
            if d in cell_directions
        }

    def build(self, start):
        current_cell = start
        while [c for c in self.cells.values() if not c & VISITED]:
            self.cells[current_cell] |= VISITED
            eligible_neighbours = self.eligible_neighbours(*current_cell)
            if not eligible_neighbours:
                next_cell = self.stack.pop()
            else:
                self.stack.append(current_cell)
                next_cell, direction = random.choice(eligible_neighbours)
                self.cells[current_cell] |= CONNECTED[direction]
                self.cells[next_cell] |= CONNECTED[ANTIPODES[direction]]
            current_cell = next_cell

    def track(self, start=(0, 0)):
        yield start
        current_cell = start
        self.stack = []
        for coord in self.cells.keys():
            self.cells[coord] &= ~VISITED
        while [c for c in self.cells.values() if not c & VISITED]:
            self.cells[current_cell] |= VISITED
            eligible_neighbours = [
                (c, d)
                for (c, d) in self.connected_cells(*current_cell).items()
                if not self.cells[c] & VISITED
            ]
            if not eligible_neighbours:
                next_cell = self.stack.pop()
            else:
                self.stack.append(current_cell)
                next_cell, direction = random.choice(eligible_neighbours)
            yield next_cell
            current_cell = next_cell

    def __repr__(self):
        buffer = [
            [0 for _ in range(2 * self.width + 1)] for _ in range(2 * self.height + 1)
        ]
        for row in range(self.height):  # 0 -> 3
            for col in range(self.width):  # 0 -> 21
                if row != 0:
                    buffer[2 * row][2 * col + 1] = (
                        ~self.cells[row, col] & CONNECTED["N"]
                    ) << 3
                if col != 0:
                    buffer[2 * row + 1][2 * col] = (
                        ~self.cells[row, col] & CONNECTED["W"]
                    ) >> 3
                if (row and col) != 0:
                    buffer[2 * row][2 * col] = (
                        buffer[2 * row][2 * col - 1]
                        | (buffer[2 * row][2 * col + 1] >> 1)
                        | buffer[2 * row - 1][2 * col]
                        | (buffer[2 * row + 1][2 * col] << 1)
                    )

        for row in range(1, 2 * self.height):
            buffer[row][0] = CONNECTED["N"] | CONNECTED["S"] | (buffer[row][1] >> 1)
            buffer[row][2 * self.width] = (
                CONNECTED["N"] | CONNECTED["S"] | buffer[row][2 * self.width - 1]
            )
        for col in range(1, 2 * self.width):
            buffer[0][col] = CONNECTED["E"] | CONNECTED["W"] | (buffer[1][col] << 1)
            buffer[2 * self.height][col] = (
                CONNECTED["E"] | CONNECTED["W"] | buffer[2 * self.height - 1][col]
            )
        buffer[0][0] = CONNECTED["S"] | CONNECTED["E"]
        buffer[0][2 * self.width] = CONNECTED["S"] | CONNECTED["W"]
        buffer[2 * self.height][0] = CONNECTED["N"] | CONNECTED["E"]
        buffer[2 * self.height][2 * self.width] = CONNECTED["N"] | CONNECTED["W"]
        finalstr = "\n".join(["".join(WALL[cell] for cell in row) for row in buffer])
        broken = list(finalstr)
        broken[len(broken) - 2 - (2 * self.width + 1)] = " "
        finalstr = "".join(broken)
        return finalstr


def path(maze, start, finish):  # Not used
    heuristic = lambda node: abs(node[0] - finish[0]) + abs(node[1] - finish[1])
    nodes_to_explore = [start]
    explored_nodes = set()
    parent = {}
    global_score = defaultdict(lambda: float("inf"))
    global_score[start] = 0
    local_score = defaultdict(lambda: float("inf"))
    local_score[start] = heuristic(start)

    def retrace_path(current):
        total_path = [current]
        while current in parent.keys():
            current = parent[current]
            total_path.append(current)
        return reversed(total_path)

    while nodes_to_explore:
        nodes_to_explore.sort(key=lambda n: local_score[n])
        current = nodes_to_explore.pop()
        if current == finish:
            return retrace_path(current)
        explored_nodes.add(current)
        for neighbour in maze.connected_cells(*current).keys():
            tentative_global_score = global_score[current] + 1
            if tentative_global_score < global_score[neighbour]:
                parent[neighbour] = current
                global_score[neighbour] = tentative_global_score
                local_score[neighbour] = global_score[neighbour] + heuristic(neighbour)
                if neighbour not in explored_nodes:
                    nodes_to_explore.append(neighbour)


def draw_path(path, screen, delay=0, head=None, trail=None, skip_first=True, calledby=None):
    if not head:
        head = ("█", curses.color_pair(2))
    if not trail:
        trail = ("█", curses.color_pair(2))
    current_cell = next(path)
    old_cell = current_cell
    for idx, next_cell in enumerate(path):
        first = (not idx) and skip_first
        if calledby != "reset" and screen.getch() == ord(" "):
            break
        screen.refresh()
        for last, cell in enumerate(
            [
                (
                    current_cell[0] + t * (next_cell[0] - current_cell[0]),
                    current_cell[1] + t * (next_cell[1] - current_cell[1]),
                )
                for t in [0, 1 / 2]
            ]
        ):
            time.sleep(delay)
            if not first:
                screen.addstr(*coords(cell), *head)
            if last:
                if not first:
                    screen.addstr(*coords(current_cell), *trail)
                old_cell = cell
            elif not first:
                screen.addstr(*coords(old_cell), *trail)
            screen.refresh()
        current_cell = next_cell


def coords(node):
    return (int(2 * node[0]) + 1, int(2 * node[1]) + 1)


def construction_demo(maze, screen):
    head = (".", curses.color_pair(3))
    trail = (".", curses.color_pair(2))
    draw_path(
        maze.track(), screen, delay=0.01, head=head, trail=trail, skip_first=False
    )
    screen.nodelay(False)


def pathfinding_demo(maze, screen, start_ts, won_coords, loadedcoords=None, loadedtime=0):
    start = []
    finish = []
    solution = None
    old_solution = None
    def reset(start_or_finish, cell, colour):
        nonlocal solution, old_solution
        if start_or_finish:
            screen.addstr(*coords(start_or_finish.pop()), " ")
        screen.addstr(*coords(cell), "█", colour)
        screen.refresh()
        if old_solution:
            draw_path(old_solution, screen, head=" ", trail=" ", calledby="reset")
        start_or_finish.append(cell)
        if start and finish:
            solution, old_solution = tee(path(maze, start[0], finish[0]))
            draw_path(solution, screen, calledby="reset") 
    maxy, maxx = screen.getmaxyx()
    
    if loadedcoords:
        current_coords = list(loadedcoords)
        cell = (int(current_coords[0] / 2), int(current_coords[1] / 2))
        reset(finish, cell, curses.color_pair(2))
        reset(start, (0,0), curses.color_pair(2))
    else:
        #current_coords = [maxy - 5, maxx - 27]
        current_coords = [1, 1]
    screen.addstr(current_coords[0], current_coords[1], "█", curses.color_pair(2))
    WALL = ["═", "║", "╗", "╚", "╝", "╔", "╠", "╣", "╦", "╩", "╬", "═", "═", "║", "║"]
    pause_elapsed = 0

    while True:
        global PAUSED
        if PAUSED:
            start_paused_ts = time.time()
            screen.addstr(4, maxx - 17, "PAUSED")
            screen.refresh()
            while True:
                pausekey = screen.getch()
                if pausekey == ord("r"):
                    end_paused_ts = time.time()
                    screen.addstr(4, maxx - 17, "      ")
                    PAUSED = False
                    break
            pause_elapsed += int(end_paused_ts - start_paused_ts)
        actual_elapsed = str(int(time.time() - start_ts - -1*loadedtime) - pause_elapsed)
        screen.addstr(5, maxx - 17, actual_elapsed + " sec")
        screen.refresh()
        key = screen.getch()
        # print("Max=",maxy, maxx, "Current=", current_coords[0], current_coords[1])
        if key == 27:
            break
        elif key == ord("p"):
            PAUSED = True
            continue
        elif key == ord("m"):
            sl.save(screen, maze, current_coords, float(actual_elapsed))
        elif current_coords[0] == won_coords[0] and current_coords[1] == won_coords[1]:
            screen.clear()
            screen.refresh()
            screen.addstr(
                0,
                0,
                """

██    ██  ██████  ██    ██     ██     ██  ██████  ███    ██ ██
 ██  ██  ██    ██ ██    ██     ██     ██ ██    ██ ████   ██ ██
  ████   ██    ██ ██    ██     ██  █  ██ ██    ██ ██ ██  ██ ██
   ██    ██    ██ ██    ██     ██ ███ ██ ██    ██ ██  ██ ██
   ██     ██████   ██████       ███ ███   ██████  ██   ████ ██



""",
            )
            screen.refresh()
            global WON
            WON = WON + 1
            time.sleep(3)
            break
        # Mouse hacks
        # elif key == curses.KEY_MOUSE:
        #     _, x, y, _, state = curses.getmouse()
        #     cell = (int(y / 2), int(x / 2))
        #     if state & curses.BUTTON3_PRESSED:
        #         reset(finish, cell, curses.color_pair(2))
        #     elif state & curses.BUTTON1_PRESSED:
        #         reset(start, cell, curses.color_pair(3))

        elif key == curses.KEY_UP:
            if (
                screen.instr(current_coords[0] - 1, current_coords[1], 1).decode(
                    "utf-8"
                )
                == "█"
            ):
                screen.addstr(current_coords[0], current_coords[1], " ")
                screen.refresh()
                current_coords = [current_coords[0] - 1, current_coords[1]]
            elif (
                screen.instr(current_coords[0] - 1, current_coords[1], 1).decode(
                    "utf-8"
                )
                not in WALL
            ):
                #    if current_coords[0]-1 != 0:
                current_coords = [current_coords[0] - 1, current_coords[1]]
                screen.addstr(
                    current_coords[0], current_coords[1], "█", curses.color_pair(2)
                )
            # else:
            #    print(screen.instr(current_coords[0]-1,current_coords[1],1).decode("utf-8"), "UP PRESS")
        elif key == curses.KEY_DOWN:
            if (
                screen.instr(current_coords[0] + 1, current_coords[1], 1).decode(
                    "utf-8"
                )
                == "█"
            ):
                screen.addstr(current_coords[0], current_coords[1], " ")
                screen.refresh()
                current_coords = [current_coords[0] + 1, current_coords[1]]
            elif (
                screen.instr(current_coords[0] + 1, current_coords[1], 1).decode(
                    "utf-8"
                )
                not in WALL
            ):
                current_coords = [current_coords[0] + 1, current_coords[1]]
                screen.addstr(
                    current_coords[0], current_coords[1], "█", curses.color_pair(2)
                )
            # else:
            #    print(screen.instr(current_coords[0]+1,current_coords[1],1).decode("utf-8"), "DOWN PRESS")
        elif key == curses.KEY_LEFT:
            if (
                screen.instr(current_coords[0], current_coords[1] - 1, 1).decode(
                    "utf-8"
                )
                == "█"
            ):
                screen.addstr(current_coords[0], current_coords[1], " ")
                screen.refresh()
                current_coords = [current_coords[0], current_coords[1] - 1]
            elif (
                screen.instr(current_coords[0], current_coords[1] - 1, 1).decode(
                    "utf-8"
                )
                not in WALL
            ):
                current_coords = [current_coords[0], current_coords[1] - 1]
                screen.addstr(
                    current_coords[0], current_coords[1], "█", curses.color_pair(2)
                )
            # else:
            #    print(screen.instr(current_coords[0],current_coords[1]-1,1).decode("utf-8"), "SIDE PRESS")
        elif key == curses.KEY_RIGHT:
            if (
                screen.instr(current_coords[0], current_coords[1] + 1, 1).decode(
                    "utf-8"
                )
                == "█"
            ):
                screen.addstr(current_coords[0], current_coords[1], " ")
                screen.refresh()
                current_coords = [current_coords[0], current_coords[1] + 1]
            elif (
                screen.instr(current_coords[0], current_coords[1] + 1, 1).decode(
                    "utf-8"
                )
                not in WALL
            ):
                current_coords = [current_coords[0], current_coords[1] + 1]
                screen.addstr(
                    current_coords[0], current_coords[1], "█", curses.color_pair(2)
                )
            # else:
            #    print(screen.instr(current_coords[0],current_coords[1]+1,1).decode("utf-8"), "RSIDE PRESS")


def menu(screen):
    y, x = screen.getmaxyx()
    screen.clear()
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
        key = screen.getch()
        if key == ord(" "):
            play(screen)
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
                    play(screen, maze[0], maze[1], maze[2])
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


def play(screen, loadedmaze=None, loadedcoords=None, loadedtime=0):
    y, x = screen.getmaxyx()
    height, width = int((y - 2) / 2), int((x - 2) / 2)
    screen.clear()
    screen.refresh()
    if not loadedmaze:
        maze = Maze(height, width)
    else:
        maze = loadedmaze
    screen.addstr(0, 0, str(maze))
    won_coords = screen.getyx()
    won_coords = list(won_coords)
    won_coords[0] = won_coords[0] - 1
    won_coords = tuple(won_coords)
    screen.refresh()
    sx = x - 22  # x - 23
    screen.addstr(0, sx, "LABYRINTH")
    screen.addstr(5, sx, "Time:")
    screen.addstr(8, sx, "esc - Quit")
    screen.addstr(9, sx, "Up - Move up")
    screen.addstr(10, sx, "Down - Move down")
    screen.addstr(11, sx, "Left - Move left")
    screen.addstr(12, sx, "Right - Move right")
    screen.addstr(13, sx, "p - Pause")
    screen.addstr(14, sx, "r - Resume")
    screen.addstr(15, sx, "m - save")
    screen.refresh()
    start_ts = time.time()
    pathfinding_demo(maze, screen, start_ts, won_coords, loadedcoords, loadedtime)
    end_ts = time.time()
    came_out = 1
    while True:
        if came_out != 0:
            screen.clear()
            screen.refresh()
            screen.erase()
            global WON
            if WON != 0:
                tt = (start_ts - end_ts) / 300
                score = fabs(cos(tt * pi))
                score *= 10000
                WON = 0
            else:
                score = 0
            screen.addstr(
                y // 2 - 5, x // 2 - 8, str("Your score is: " + str(int(score)))
            )
            res = database.Update_score(int(score))
            if res == "guest":
                screen.addstr(
                    height - 1,
                    5,
                    "You are not signed in. You will lose your score if you proceed.",
                )
                screen.addstr(
                    height, 5, "Do you want to login and save your progress? (y/n)"
                )
                while True:
                    key = screen.getch()
                    if key == ord("y"):
                        database.login(screen, calledby=int(score))
                        break
                    elif key == ord("n"):
                        break
            screen.clear()
            screen.refresh()
            came_out = 0
            menu(screen)
            return


def main(screen):
    curses.curs_set(False)
    curses.mousemask(curses.ALL_MOUSE_EVENTS)
    screen.nodelay(True)
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    screen.clear()
    screen.refresh()
    y, x = screen.getmaxyx()
    height, width = int((y - 2) / 2), int((x - 2) / 2)
    database.databaseinit()
    database.tableinit()
    maze = Maze(height, width)
    screen.addstr(0, 0, str(maze))
    screen.refresh()
    screen.addstr(2, x - 22, "Press space to skip")
    screen.addstr(3, x - 22, "the loading screen...")
    construction_demo(maze, screen)
    screen.clear()
    screen.refresh()  # 70x 15y
    menu(screen)
    exit()
