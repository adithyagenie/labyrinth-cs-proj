import curses
import os
import random
import re
import string
from base64 import b64decode, b64encode
from time import sleep

import mysql.connector

import maze.modules.maze

from .password_forget import sender

loggedin = False
U = gamerid = None
quitting = False

sql = con = None


def get(
    query,
):  # Simplifed function to fetch records from mysql instead of typing fetchall over nd over
    con.execute(query)
    r = con.fetchall()
    return r


def post(
    query,
):  # Simplifed function to commit queries to mysql instead of typing this again and again
    con.execute(query)
    try:
        sql.commit()
    except:
        print("ERROR OCCURED COMMITTING CHANGES")


def databaseinit():  # Creates database if it doesn't exist
    try:
        tempsql = mysql.connector.connect(host="localhost", user="root", passwd="root")
        tempcon = tempsql.cursor()
        tempcon.execute("CREATE DATABASE IF NOT EXISTS labyrinth")
        tempsql.commit()

        global sql, con
        sql = mysql.connector.connect(
            host="localhost", user="root", passwd="root", database="labyrinth"
        )
        con = sql.cursor()
        return True
    except (
        mysql.connector.errors.ProgrammingError,
        mysql.connector.errors.DatabaseError,
    ):
        print("Invalid password/username.")
        return False


def tableinit():
    try:
        post(
            "CREATE TABLE IF NOT EXISTS player_details\
    (\
        gamerid  CHAR(4) PRIMARY KEY,\
        username VARCHAR(32) NOT NULL,\
        email    VARCHAR(32) NOT NULL,\
        password VARCHAR(32) NOT NULL\
    )  "
        )

        post(
            "CREATE TABLE IF NOT EXISTS scores\
        (\
        gamerid     CHAR(4) PRIMARY KEY,\
        highscore   INT,\
        lastplayed  DATE,\
        timesplayed INT\
        )  "
        )
    except Exception as e:
        print(e)
        print("ERROR: Creating Table(s)")


def screenhandler(screen):  # MAIN MENU
    h, w = screen.getmaxyx()
    global loggedin, U, gamerid
    screen.clear()
    screen.refresh()
    screen.addstr(1, w // 2 - 8, "ACCOUNT SETTINGS")
    if loggedin:
        screen.addstr(2, w // 2 - 8, f"Logged in as: {U}")
    screen.addstr(h // 2 - 3, w // 2 - 4, "1. Login")
    screen.addstr(h // 2 - 2, w // 2 - 8, "2. Create Account")
    screen.addstr(h // 2 - 1, w // 2 - 12, "3. Modify account details")
    screen.addstr(h // 2 - 0, w // 2 - 12, "4. View account details")
    screen.addstr(h // 2 + 1, w // 2 - 8, "5. Delete Account")
    if not loggedin:
        screen.addstr(h // 2 + 2, w // 2 - 9, "6. Forgot Password?")
        screen.addstr(h // 2 + 3, w // 2 - 3, "esc. Quit")
    else:
        screen.addstr(h // 2 + 2, w // 2 - 3, "6. Logout")
        screen.addstr(h // 2 + 3, w // 2 - 3, "esc. Quit")
    screen.border()
    screen.refresh()
    while True:
        key = screen.getch()
        if key == ord("1"):
            login(screen)
        elif key == ord("2"):
            new_add(screen)
        elif key == ord("3"):
            modify_account(screen)
        elif key == ord("4"):
            view_account(screen)
        elif key == ord("5"):
            delete(screen)
        elif key == ord("6"):
            if not loggedin:
                forgotpassword(screen)
            elif loggedin:
                logout(screen)
        elif key == 27:
            maze.modules.maze.menu(screen)
            break
    screen.refresh()


def screenwipe(screen, sx, sy):  # Failed password and stuff reset from screen
    y, x = screen.getmaxyx()
    for i in range(sx, x):
        screen.addstr(sy, i, " ")
    for i in range(sy + 1, y - 1):
        for j in range(0, x - 1):
            if screen.instr(i, j, 1) != " ":
                screen.addstr(i, j, " ")
    screen.border()
    screen.refresh()


def input(
    y, x, screen, ispassword=False
):  # Function to get type-able inputs, with delete, esc and other keys
    inputted = ""
    orig_y, orig_x = y, x
    while True:
        key = screen.getch()
        if key == 10:
            break
        elif key == 8:
            if x > orig_x:
                x -= 1
                screen.addstr(y, x, " ")
                inputted = inputted[: len(inputted) - 1]
        elif key == 27:
            global quitting
            quitting = True
            break
        else:
            inputted += chr(key)
            if ispassword:
                screen.addstr(y, x, "*")
            else:
                screen.addstr(y, x, chr(key))
            x += 1

    return inputted


def list_getter(field):  # Feed in the field name you want, get all records of it
    index = {"username": 1, "email": 2, "password": 3}
    return_list = []
    res = get("SELECT * FROM player_details")
    for i in res:
        return_list.append(i[index[field]])
    return return_list


def login(screen, calledby=False):  # Function to log in
    global quitting, U, gamerid, loggedin
    screen.clear()
    screen.refresh()
    screen.border()
    y, x = screen.getmaxyx()
    usernamelist = list_getter("username")
    screen.addstr(1, x // 2 - 3, "LOGIN")
    screen.addstr(y // 2 - 2, x // 2 - 7, "Username: ")
    while True:
        inputU = input(y // 2 - 2, x // 2 + 3, screen)
        if quitting:
            screen.addstr("Going back to account settings...")
            sleep(3)
            quitting = False
            screen.clear()
            screen.refresh()
            screenhandler(screen)
            return
        if inputU not in usernamelist:
            screen.addstr(
                y // 2, 5, "Username does not exist. Do you want to create one? (y/n)"
            )
            while True:
                key = screen.getch()
                if key == ord("y"):
                    if calledby:
                        new_add(screen, calledby=calledby)
                    else:
                        new_add(screen)
                    return
                elif key == ord("n"):
                    screenwipe(screen, x // 2 + 3, y // 2 - 2)
                    break
        else:
            break

    res = get(
        f"SELECT password,\
        gamerid\
        FROM   player_details\
        WHERE  username = '{inputU}'  "
    )
    actualpass = (b64decode(res[0][0].encode("ascii"))).decode("ascii")
    screen.addstr(y // 2, x // 2 - 7, "Password: ")
    while True:
        inputP = input(y // 2, x // 2 + 3, screen, ispassword=True)
        if quitting:
            screen.addstr(y // 2 + 3, 5, "Going back to account settings...")
            sleep(3)
            screen.clear()
            screen.refresh()
            screenhandler(screen)
        if inputP == actualpass:
            loggedin = True
            gamerid = res[0][1]
            U = inputU
            screen.addstr(y // 2 + 2, x // 2 - 4, "Login Successful!")
            if calledby:
                screen.addstr(y // 2 + 3, x // 2 - 4, "Updating score...")
                screen.refresh()
                sleep(3)
                Update_score(calledby)
                return
            else:
                screen.addstr(y // 2 + 3, x // 2 - 4, "Returning to menu screen...")
                screen.refresh()
                sleep(3)
                screenhandler(screen)
                return
        else:
            screen.addstr(y // 2 + 2, x // 2 - 4, "Wrong password. Try again.")
            while True:
                key = screen.getch()
                if key == 10:
                    screenwipe(screen, sx=x // 2 + 3, sy=y // 2)
                    screen.refresh()
                    break
            continue


def user(
    screen, sy, sx, optionaltxt="Enter username: "
):  # Function to get new username for account creation
    if quitting:
        screen.clear()
        screen.refresh()
        return
    screen.refresh()
    userlist = list_getter("username")
    screen.addstr(sy, sx, optionaltxt)
    while True:
        Name = input(sy, sx + len(optionaltxt), screen)
        if quitting:
            screen.clear()
            screen.refresh()
            return
        if Name in userlist:
            screen.addstr(
                sy + 1, 5, "Username already exists, please choose a different one"
            )
            while True:
                key = screen.getch()
                if key == 10:
                    screenwipe(screen, sx=sx + len(optionaltxt), sy=sy)
                    screen.refresh()
                    break
            continue
        else:
            break

    return Name


def password(screen, sy, sx, optionaltxt="Enter Password: "):
    if quitting:
        screen.clear()
        screen.refresh()
        return
    sl, su, p = 0, 0, 0
    screen.refresh()
    while True:
        screen.addstr(sy, sx, optionaltxt)
        Password = input(sy, sx + len(optionaltxt), screen, ispassword=True)
        if quitting:
            screen.clear()
            screen.refresh()
            return
        for i in Password:
            if i.islower():
                sl += 1
            elif i.isupper():
                su += 1
            elif i.isdigit():
                p += 1
        if sl >= 1 and su >= 1 and p >= 1 and len(Password) <= 10:
            break
        else:
            screen.addstr(sy + 1, sx + 2, "Invalid Password")
            screen.addstr(sy + 2, 5, "Password must contain uppercase, lowercase and")
            screen.addstr(sy + 3, 5, "digits and should be lesser than 10 characters")
            while True:
                key = screen.getch()
                if key == 10:
                    screenwipe(screen, sx=sx + len(optionaltxt), sy=sy)
                    screen.refresh()
                    break
            continue

    encoded_pass = (b64encode(Password.encode("ascii"))).decode("ascii")
    return encoded_pass


def email(screen, sy, sx, optionaltxt="Enter Email: "):  # Function to accept email id
    if quitting:
        screen.clear()
        screen.refresh()
        return
    ev = re.compile(r"[a-z0-9]+@[a-z]+\.[a-z]{2,3}")
    emailist = list_getter("email")
    y, x = screen.getmaxyx()
    screen.refresh()
    while True:
        screen.addstr(sy, sx, optionaltxt)
        email = input(sy, sx + len(optionaltxt), screen)
        if quitting:
            screen.clear()
            screen.refresh()
            return
        if email in emailist:
            screen.addstr(
                sy + 1, sx, "Given email already exists. Enter a different email."
            )
            while True:
                key = screen.getch()
                if key == 10:
                    screenwipe(screen, sx=sx + len(optionaltxt), sy=sy)
                    screen.refresh()
                    break
            continue
        else:
            if ev.match(email):
                break
            else:
                screen.addstr(y // 2 + 1, x // 2 - 5, "Invalid Email")
                while True:
                    key = screen.getch()
                    if key == 10:
                        screenwipe(screen, sx=x // 2 + 3, sy=y // 2)
                        screen.refresh()
                        break
                continue
    return email


def new_add(screen, calledby=False):
    screen.clear()
    screen.refresh()
    screen.border()
    y, x = screen.getmaxyx()
    global quitting
    screen.addstr(1, x // 2 - 8, "ACCOUNT CREATION")
    add_name = user(
        screen, y // 2 - 4, x // 2 - 10
    )  # calling fn user for username, password and email
    add_password = password(screen, y // 2 - 2, x // 2 - 10)
    add_email = email(screen, y // 2, x // 2 - 10)
    add_gamerid = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=4)
    )  # Generates random 4 character alphanumeric

    if add_name == None or add_password == None or add_email == None:
        screen.refresh()
        screen.addstr(
            y // 2 + 2, 5, "Cancelling account creation. Returning to account menu..."
        )
        sleep(3)
        screen.clear()
        screen.refresh()
        quitting = False
        screenhandler(screen)
    else:
        post(
            f"INSERT INTO player_details\
                (gamerid,\
                 username,\
                 email,\
                 password)\
            VALUES      ('{add_gamerid}',\
                         '{add_name}',\
                         '{add_email}',\
                         '{add_password}')"
        )
        screen.refresh()
        if calledby:
            screen.addstr(
                y // 2 + 2, 5, "Account has been created. Returning to login..."
            )
            screen.refresh()
            sleep(3)
            login(screen, calledby=calledby)
        else:
            screen.addstr(
                y // 2 + 2, 5, "Account has been created. Returning to account menu..."
            )
            screen.refresh()
            sleep(3)
            screenhandler(screen)


def modify_account(screen):
    screen.clear()
    screen.refresh()
    screen.border()
    y, x = screen.getmaxyx()
    global loggedin, quitting, U
    screen.addstr(1, x // 2 - 8, "MODIFY ACCOUNT SETTINGS")
    if loggedin == False:
        screen.addstr(
            y // 2,
            5,
            "Please log in to you account... Redirecting you to the login menu",
        )
        screen.refresh()
        sleep(3)
        login(screen)
        return
    screen.addstr(3, x // 2 - 8, "What do you want to modify?")
    screen.addstr(y // 2 - 3, x // 2 - 4, "1. Username")
    screen.addstr(y // 2 - 1, x // 2 - 4, "2. Email")
    screen.addstr(y // 2 + 1, x // 2 - 4, "esc. Quit")

    while True:
        key = screen.getch()
        if key == 27:
            break

        elif key == ord("1"):
            screenwipe(screen, 0, 2)
            screen.refresh()
            newuser = user(
                screen,
                y // 2,
                x // 2 - 10,
                optionaltxt="Enter new username: ",
            )
            post(
                f"UPDATE player_details\
                    SET    username = '{newuser}'\
                    WHERE  gamerid = '{gamerid}'  "
            )
            U = newuser
            break

        elif key == ord("2"):
            screenwipe(screen, 0, 2)
            screen.refresh()
            newemail = email(
                screen, y // 2, x // 2 - 10, optionaltxt="Enter new email: "
            )
            post(
                f"UPDATE player_details\
                    SET    email = '{newemail}'\
                    WHERE  gamerid = '{gamerid}'  "
            )
            break

    screenwipe(screen, 0, 2)
    screen.refresh()
    screen.addstr(
        y // 2, 5, "Details successfully updated. Returning to account menu..."
    )
    screen.refresh()
    sleep(3)
    screenhandler(screen)
    return


def view_account(screen):
    global loggedin, U, gamerid
    y, x = screen.getmaxyx()
    screen.clear()
    screen.refresh()
    screen.border()
    screen.addstr(1, x // 2 - 6, "VIEW ACCOUNT DETAILS")
    if not loggedin:
        screen.addstr(
            y // 2,
            5,
            "Please log in to you account... Redirecting you to the login menu",
        )
        screen.refresh()
        sleep(3)
        login(screen)
        return
    player_details = get(
        f"SELECT *\
                            FROM   player_details\
                            WHERE  gamerid = '{gamerid}'  "
    )
    score_details = get(f"SELECT * FROM scores WHERE gamerid = '{gamerid}'")
    screen.addstr(y // 2 - 4, x // 2 - 5, "Gamer ID: " + player_details[0][0])
    screen.addstr(y // 2 - 2, x // 2 - 5, "Username: " + player_details[0][1])
    screen.addstr(y // 2, x // 2 - 5, "Email: " + player_details[0][2])
    if not score_details:
        score_details.append(("Bruh",) + ("Not yet available.",) * 3)
    screen.addstr(y // 2 + 2, x // 2 - 5, "High Score: " + str(score_details[0][1]))
    screen.addstr(y // 2 + 4, x // 2 - 5, "Last Played: " + str(score_details[0][2]))
    screen.addstr(y // 2 + 6, x // 2 - 5, "Times Played: " + str(score_details[0][3]))

    screen.addstr(y - 1, 5, "Press esc to return to main menu.")
    while True:
        key = screen.getch()
        if key == 27:
            break
    screen.refresh()
    screenhandler(screen)
    return


def delete(screen):
    y, x = screen.getmaxyx()
    global loggedin, gamerid, U
    screen.clear()
    screen.refresh()
    screen.border()
    if loggedin == False:
        screen.addstr(
            y // 2,
            5,
            "Please log in to you account... Redirecting you to the login menu",
        )
        screen.refresh()
        sleep(3)
        login(screen)
        return
    screen.addstr(y // 2 - 3, 10, "Do you really want to delete your account?")
    screen.addstr(y // 2 - 2, 10, "Press y to delete or n to return to account menu.")
    while True:
        key = screen.getch()
        if key == ord("y"):
            break
        elif key == ord("n"):
            screen.addstr(y // 2, 5, "Returning to the account menu")
            sleep(3)
            screenhandler(screen)
            return
    post(
        f"DELETE FROM player_details\
         WHERE  gamerid = '{gamerid}'"
    )
    curses.ungetch(" ")
    screen.addstr(y // 2, 10, "Account has been deleted. Returning to account menu...")
    screen.refresh()
    loggedin = False
    gamerid = U = None
    sleep(3)
    screenhandler(screen)
    return


def Update_score(Score):
    global U, gamerid, loggedin
    if not loggedin:
        return "guest"
    res = get(f"SELECT * FROM scores WHERE gamerid = '{gamerid}'")
    if not res:
        post(f"INSERT INTO scores (gamerid, timesplayed) VALUES ('{gamerid}', 0)")
        # implement to ask whether to update
    post(
        f"UPDATE scores\
         SET    highscore = '{Score}'\
         WHERE gamerid = '{gamerid}'"
    )
    Update_lp_tp()


def Update_lp_tp():
    global U, gamerid, loggedin
    if not loggedin:
        return "guest"
    post(
        f"UPDATE scores\
        SET    lastplayed = Now(),\
        timesplayed = timesplayed + 1\
        WHERE gamerid = '{gamerid}'"
    )


def forgotpassword(screen):
    screen.clear()
    screen.refresh()
    y, x = screen.getmaxyx()
    screen.addstr(1, x // 2 - 7, "FORGOT PASSWORD")
    screen.refresh()
    global quitting
    usernamelist = list_getter("username")
    tries = 0
    screen.addstr(y // 2 - 2, x // 2 - 7, "Username: ")
    while True:
        input_u = input(y // 2 - 2, x // 2 + 3, screen)
        if quitting:
            screen.addstr("Going back to account settings...")
            sleep(3)
            quitting = False
            screen.clear()
            screen.refresh()
            screenhandler(screen)
            return

        if input_u not in usernamelist:
            screen.addstr(
                y // 2 - 1,
                5,
                "Username does not exist. Press Enter/Space to continue...",
            )
            while True:
                key = screen.getch()
                if key == ord(" ") or key == 10:
                    screenwipe(screen, sy=y // 2 - 2, sx=x // 2 + 3)
                    screen.refresh()
                    break
        else:
            break

    res = get(
        f"SELECT email FROM player_details\
                WHERE username = '{input_u}'"
    )
    email = res[0][0]
    otp = sender(input_u, email)
    screen.addstr(y // 2 + 1, 5, "Enter OTP recieved in registered mail address:")
    while True:
        screen.refresh()
        enter_otp = input(y // 2 + 1, 47, screen)
        if quitting:
            screen.addstr("Going back to account settings...")
            sleep(3)
            quitting = False
            screen.clear()
            screen.refresh()
            screenhandler(screen)
            return
        if str(otp) == enter_otp:
            screen.clear()
            screen.refresh()
            screen.addstr(1, x // 2 - 7, "FORGOT PASSWORD")
            while True:
                enter_pass = password(
                    screen, y // 2 - 2, x // 2 - 7, optionaltxt="Enter new password: "
                )
                confirm_pass = password(
                    screen, y // 2 + 1, x // 2 - 7, optionaltxt="Confirm password: "
                )
                if enter_pass == confirm_pass:
                    break
                else:
                    screen.addstr(
                        y // 2 + 3,
                        5,
                        "Passwords do not match. Press Enter to try again.",
                    )
                    while True:
                        key = screen.getch()
                        if key == 10:
                            screenwipe(screen, sy=y // 2 - 2, sx=x // 2 - 7)
                            break
        else:
            if tries < 10:
                screen.addstr(
                    y // 2 + 3,
                    5,
                    "Entered OTP is wrong. Press esc to exit or Enter to try again.",
                )
                while True:
                    key = screen.getch()
                    if key == 10:
                        screenwipe(screen, sy=y // 2 + 1, sx=47)
                        tries += 1
                        screen.refresh()
                        break
                    elif key == 27:
                        screen.clear()
                        screen.refresh()
                        screenhandler(screen)
                        return
                continue

            else:
                screen.addstr(
                    y // 2 + 3,
                    5,
                    "Entered OTP is wrong. Maximum tries exceeded. Returning to account menu...",
                )
                sleep(5)
                screen.clear()
                screen.refresh()
                screenhandler(screen)
                return
        break

    post(
        f"UPDATE player_details\
        SET password = '{enter_pass}'\
        WHERE username = '{input_u}'"
    )
    screen.addstr(y // 2 + 3, x // 2 - 10, "Password has been changed successfully.")
    screen.addstr(y // 2 + 4, x // 2 - 8, "Returning to account menu...")
    sleep(3)
    screenhandler(screen)
    return


def logout(screen):
    y, x = screen.getmaxyx()
    screen.clear()
    screen.refresh()
    screen.addstr(1, x // 2 - 2, "LOGOUT")
    screen.addstr(y // 2, 5, "Logging out of your account...")
    global loggedin, U, gamerid
    loggedin = False
    U = gamerid = None
    screen.refresh()
    sleep(5)
    screen.clear()
    screen.refresh()
    screenhandler(screen)
    return


def leaderboard(screen):
    y, x = screen.getmaxyx()
    screen.clear()
    screen.border()
    screen.addstr(1, x // 2 - 5, "LEADERBOARD")
    screen.refresh()
    res = get(
        "SELECT p.gamerid,\
                p.username,\
                s.highscore,\
                s.lastplayed\
                FROM    player_details p,\
                        scores s\
                WHERE   p.gamerid = s.gamerid  "
    )

    for i in range(len(res) - 1):
        for j in range(len(res) - 1 - i):
            if res[j][2] < res[j + 1][2]:
                res[j], res[j + 1] = res[j + 1], res[j]

    screen.addstr(3, 13, "GamerID")
    screen.addstr(3, 30, "Username")
    screen.addstr(3, 50, "High Score")
    screen.addstr(3, 70, "Last Played")
    sy = 5
    for i in res:
        screen.addstr(sy, 13, str(i[0]))
        screen.addstr(sy, 30, str(i[1]))
        screen.addstr(sy, 50, str(i[2]))
        screen.addstr(sy, 70, str(i[3]))
        sy += 1
    screen.addstr(y - 1, x - 35, "Press esc to return to main menu.")
    while True:
        key = screen.getch()
        if key == 27:
            break
    screen.refresh()
    maze.modules.maze.menu(screen)
    return
