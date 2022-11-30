import curses
import random
import threading
import time
from math import fabs

import maze.modules.maze as m1

quit = threading.Event()


class Scores:
    def __init__(self, screen):
        self.score = 0
        self.screen = screen
        self.collision_count = 0
        self.speed_multiplier = 0.20
        self.speed_calc = lambda speed: speed - 0.02 if self.score % 30 == 0 else speed

    def scoreupdate(self):
        self.score += 10
        self.collision_count += 1
        self.speed_multiplier = self.speed_calc(self.speed_multiplier)
        self.scoreupdater()
        return self.speed_multiplier

    def scoreupdater(self):
        y, x = self.screen.getmaxyx()
        self.screen.addstr(0, x - 5, str(self.score))


class Ball:
    def __init__(self, y, x, screen):
        self.ball_dx = 1
        self.ball_dy = 1
        self.speed_multipliery = random.choice([1, 2])
        self.speed_multiplierx = random.choice([1, 2])
        self.ball_dy *= self.speed_multipliery
        self.ball_dx *= self.speed_multiplierx
        self.ball_coords = [y // 2, x // 2]
        self.y = y
        self.x = x
        self.y_border = [0, y]
        self.x_border = [0, x]
        self.screen = screen

    def move(self):
        raw_calc_to_movey = lambda y: y + self.ball_dy
        raw_calc_to_movex = lambda x: x + self.ball_dx
        raw_movey = raw_calc_to_movey(
            self.ball_coords[0]
        )  # Gives raw about to move coords without speed alter
        raw_movex = raw_calc_to_movex(self.ball_coords[1])

        speed_altery = lambda y: int(y / fabs(y))  # Gives unit speed in the current dir
        speed_alterx = lambda x: int(x / fabs(x))
        calc_to_movey = (
            lambda y: y + speed_altery(self.ball_dy)
            if checky(raw_movey)
            else y + self.ball_dy
        )  # assign same dir movement coords
        calc_to_movex = (
            lambda x: x + speed_alterx(self.ball_dx)
            if checkx(raw_movex)
            else x + self.ball_dx
        )
        checky = (
            lambda y: True
            if (y in self.y_border)
            or (y >= self.y_border[1])
            or (y <= self.y_border[0] + 1)
            else False
        )  # Gives True if out of bound coords
        checkx = (
            lambda x: True
            if (x in self.x_border)
            or (x >= self.x_border[1] - 1)
            or (x <= self.x_border[0] + 1)
            else False
        )

        actual_game_checky = (
            lambda y: True if (y <= self.y_border[0]) else False
        )  # Gives true if ball at top

        to_movey = calc_to_movey(self.ball_coords[0])  # Moving here after speed alter
        to_movex = calc_to_movex(self.ball_coords[1])
        old_ball = self.ball_coords.copy()
        collision = False
        pos = self.screen.instr(to_movey, to_movex, 1).decode("utf-8")
        if pos == "=" or pos == "[" or pos == "]":
            collision = True
        if (
            actual_game_checky(to_movey) or collision
        ):  # Deflect ball if top border/collision
            self.ball_dy *= -1
        elif to_movey >= self.y_border[1] and not collision:
            return [None, None], [None, None], "OVER"
        if checkx(to_movex):
            self.ball_dx *= -1
        self.ball_coords[0] += self.ball_dy
        self.ball_coords[1] += self.ball_dx
        if collision:
            return self.ball_coords, old_ball, "collision"
        return self.ball_coords, old_ball, "nocollision"


class Player:
    def __init__(self, y, x):
        self.y = y
        self.x = x
        self.paddle = "[=======]"
        self.paddle_posx = x // 2
        self.paddle_posy = y - 1  # Top of paddle

    def player_move(self, dir):
        if dir == "LEFT" and self.paddle_posx > 1:
            self.paddle_posx -= 1
        if dir == "RIGHT" and self.paddle_posx + 10 < self.x:
            self.paddle_posx += 1
        return self.paddle_posy, self.paddle_posx


def player_movement(screen, player):
    global quit
    screen.keypad(True)
    while 1:
        # f.write("player running\n")
        if quit.is_set():
            break
        old_player_coordsy = player_coordsy = player.paddle_posy
        old_player_coordsx = player_coordsx = player.paddle_posx
        key = screen.getch()
        if key == 27:
            quit.set()
        elif key == curses.KEY_LEFT:
            player_coordsy, player_coordsx = player.player_move("LEFT")
        elif key == curses.KEY_RIGHT:
            player_coordsy, player_coordsx = player.player_move("RIGHT")
        screen.addstr(old_player_coordsy, old_player_coordsx, "         ")
        screen.addstr(player_coordsy, player_coordsx, player.paddle)


def ball_movement(screen, ball, score):
    y, x = screen.getmaxyx()
    while 1:
        # f.write("ball running\n")
        if quit.is_set():
            break
        speed_multi = score.speed_multiplier
        time.sleep(speed_multi)
        ball_coords = ball.move()
        old_ball_posy, old_ball_posx = ball_coords[1]
        ball_posy, ball_posx = ball_coords[0]
        collision = ball_coords[2]
        if collision == "OVER":
            finalscore = score.score
            screen.addstr(
                y // 2 - 1,
                x // 2 - 3,
                "GAME OVER!",
                curses.color_pair(1) | curses.A_BOLD,
            )
            screen.addstr(
                y // 2,
                x // 2 - 5,
                "The Score is: " + str(finalscore),
                curses.color_pair(3) | curses.A_BOLD,
            )
            time.sleep(0.25)
            quit.set()
            time.sleep(1.75)
            break
        elif collision == "collision":
            score.scoreupdate()
        screen.addch(old_ball_posy, old_ball_posx, " ")
        screen.addch(ball_posy, ball_posx, "⬤", curses.color_pair(1) | curses.A_BOLD)
        screen.refresh()


def main(screen):
    global quit
    quit.clear()
    screen.clear()
    screen.refresh()
    screen.nodelay(True)
    curses.curs_set(False)
    screen.keypad(True)
    y, x = screen.getmaxyx()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    screen.border(0, 0, 0, " ", 0, 0, " ", " ")
    ball = Ball(y, x, screen)
    score = Scores(screen)
    player = Player(y, x)
    ball_thread = None
    ball_thread = threading.Thread(
        target=ball_movement,
        args=(
            screen,
            ball,
            score,
        ),
    )
    player_thread = None
    player_thread = threading.Thread(
        target=player_movement,
        args=(
            screen,
            player,
        ),
    )
    screen.addstr(0, x - 13, "            ")
    screen.addstr(0, x - 12, "Score: 0")
    ball_thread.start()
    player_thread.run()
    time.sleep(1)
    m1.play(screen, executeguest=True, outerscore=score.score, outergame="pong")
    maze.menu.menu(stdscr)
    return
