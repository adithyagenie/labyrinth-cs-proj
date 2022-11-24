import maze.menu


def about(screen):
    y, x = screen.getmaxyx()
    screen.clear()
    screen.refresh()
    screen.border()
    screen.addstr(1, x // 2 - 2, "ABOUT US")
    screen.addstr(
        3,
        5,
        "This game which you have played was developed as a Computer Science Project by",
    )
    screen.addstr(5, 5, "B. Adithya\t\t\t - XII - C - Roll no: 3")
    screen.addstr(6, 5, "V. Kirthivaasan\t\t - XII - C - Roll no: 17")
    screen.addstr(7, 5, "R. Manwanthakrishnan\t - XII - C - Roll no: 21")
    screen.addstr(
        9,
        5,
        "This game aims at generating a maze which always has a path towards the right bottom corner",
    )
    screen.addstr(
        10, 5, "by using a famous generation algorithm named Depth First Search (DFS)."
    )
    screen.addstr(
        11,
        5,
        "This game makes use of the 'curses' module which runs on any operating system in the native terminal without",
    )
    screen.addstr(12, 5, "use of any other external modules.")
    screen.addstr(
        13,
        5,
        "It makes use of SQL tables to store login details and maintain a leaderboard.",
    )
    screen.addstr(
        14,
        5,
        "It also makes use of binary files to save and load mazes.",
    )
    screen.addstr(16, 5, "This project has been an absolute blast to make.")
    screen.addstr(
        17, 5, "We thank you for playing this! Hope you liked it as much as we did!"
    )
    screen.addstr(20, 5, "Signing off,")
    screen.addstr(21, 5, "The Labyrinth")
    screen.addstr(y - 2, x - 31, "Press Esc to exit this screen.")
    screen.refresh()
    while True:
        key = screen.getch()
        if key == 27:
            break
    maze.menu.menu(screen)
    return
