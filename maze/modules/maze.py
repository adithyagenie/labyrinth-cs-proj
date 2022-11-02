import curses
import time
from math import exp, pi, cos, fabs
import random
from collections import defaultdict
from itertools import tee
import maze.modules.PlayerBase_func as database

WON = 0
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
        self.width = width - 12
        self.stack = []
        self.cells = {(y, x): 0 for y in range(height) for x in range(width)}
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

        return finalstr


def path(maze, start, finish):
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


def draw_path(path, screen, delay=0.15, head=None, trail=None, skip_first=True):
    if not head:
        head = ("█", curses.color_pair(1))
    if not trail:
        trail = ("█", curses.color_pair(1))
    current_cell = next(path)
    old_cell = current_cell
    for idx, next_cell in enumerate(path):
        first = (not idx) and skip_first
        if screen.getch() == ord("q"):
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
    head = (".", curses.color_pair(2))
    trail = (".", curses.color_pair(1))
    draw_path(
        maze.track(), screen, delay=0.01, head=head, trail=trail, skip_first=False
    )
    screen.nodelay(False)
    screen.getch()


def pathfinding_demo(maze, screen, start_ts):
    start = []
    finish = []
    solution = None
    old_solution = None
    """ def reset(start_or_finish, cell, colour):
        nonlocal solution, old_solution
        if start_or_finish:
            screen.addstr(*coords(start_or_finish.pop()), " ")
        screen.addstr(*coords(cell), "█", colour)
        screen.refresh()
        if old_solution:
            draw_path(old_solution, screen, head=" ", trail=" ")
        start_or_finish.append(cell)
        if start and finish:
            solution, old_solution = tee(path(maze, start[0], finish[0]))
            draw_path(solution, screen) """
    maxy, maxx = screen.getmaxyx()
    current_coords = [maxy - 5, maxx - 35]
    screen.addstr(current_coords[0], current_coords[1], "█", curses.color_pair(2))
    WALL = ["═", "║", "╗", "╚", "╝", "╔", "╠", "╣", "╦", "╩", "╬", "═", "═", "║", "║"]
    while True:
        screen.addstr(2, maxx - 17, str(round(time.time()-start_ts, 0)) + " sec")
        screen.refresh()
        key = screen.getch()
        # print("Max=",maxy, maxx, "Current=", current_coords[0], current_coords[1])
        if key == 27:
            break
        elif current_coords[0] == maxy - 3 and current_coords[1] == maxx - 27:
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
        # Dota stuff not to be used now
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
    text = """

██       █████  ██████  ██    ██ ██████  ██ ███    ██ ████████ ██   ██
██      ██   ██ ██   ██  ██  ██  ██   ██ ██ ████   ██    ██    ██   ██
██      ███████ ██████    ████   ██████  ██ ██ ██  ██    ██    ███████
██      ██   ██ ██   ██    ██    ██   ██ ██ ██  ██ ██    ██    ██   ██
███████ ██   ██ ██████     ██    ██   ██ ██ ██   ████    ██    ██   ██

"""
    screen.addstr(1, 3, str(text))
    screen.refresh()
    screen.addstr(5, x // 2 - 2, "MENU")
    screen.addstr(10, 0, "space - Play")
    screen.addstr(11, 0, "a - Account Settings")
    screen.addstr(12, 0, "l - Leaderboard")
    screen.addstr(13, 0, "esc - Quit")
    while True:
        key = screen.getch()
        if key == ord(" "):
            play(screen)
        elif key == 27:
            screen.clear()
            screen.refresh()
            break
        elif key == ord("a"):
            database.screenhandler(screen)
        elif key == ord("l"):
            database.leaderboard(screen)


def play(screen):
    came_out = 0
    start_ts = 0
    end_ts = 0
    y, x = screen.getmaxyx()
    height, width = int((y - 2) / 2), int((x - 2) / 2)
    screen.clear()
    maze = Maze(height, width)
    screen.addstr(0, 0, str(maze))
    screen.refresh()
    screen.addstr(0, x - 23, "LABYRINTH")
    screen.addstr(2, x - 23, "Time:")
    screen.addstr(5, x - 23, "esc - Quit")
    screen.addstr(6, x - 23, "Right - Move right")
    screen.addstr(7, x - 23, "Left - Move left")
    screen.addstr(8, x - 23, "Up - Move up")
    screen.addstr(9, x - 23, "Down - Move down")
    screen.refresh()
    start_ts = time.time()
    pathfinding_demo(maze, screen, start_ts)
    end_ts = time.time()
    came_out = 1
    while True:
        key = screen.getch()
        if key == ord("q"):
            break

        if came_out != 0:
            screen.clear()
            screen.refresh()
            global WON
            if WON != 0:
                tt = (start_ts - end_ts) / 300
                score = fabs(cos(tt * pi))
                score *= 10000
                WON = 0
            else:
                score = 0
            screen.addstr(
                height - 3, width - 4, str("Your score is: " + str(int(score)))
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
            screen.refresh()
            time.sleep(3)
            screen.clear()
            menu(screen)
            came_out = 0


def main(screen):
    curses.curs_set(False)
    curses.mousemask(curses.ALL_MOUSE_EVENTS)
    screen.nodelay(True)
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    screen.clear()
    height, width = screen.getmaxyx()
    height, width = int((height - 2) / 2), int((width - 2) / 2)
    database.databaseinit()
    database.tableinit()
    maze = Maze(height, width)
    screen.addstr(0, 0, str(maze))
    screen.refresh()
    construction_demo(maze, screen)
    screen.clear()
    screen.refresh()  # 70x 15y
    menu(screen)
    exit()