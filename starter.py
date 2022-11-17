import os
import pickle
import subprocess
import sys

import mysql.connector

from maze.modules import bruh
from maze.modules.PlayerBase_func import databaseinit

with open("credentials.pickle", "rb") as f:
    try:
        while True:
            d = pickle.load(f)
            if d["credtype"] == "mysql":
                user = d["user"]
                password = d["pass"]
                break
    except EOFError:
        user = password = None


def getcreds():
    if user and password:
        return user, password
    else:
        print(
            """MySQL username or password not initialised. Defaulting to 'root' and ''.
Run 'python starter.py initsql' to initialise credentials of your choice. """
        )
        with open("credentials.pickle", "rb+") as f:
            try:
                while True:
                    pos = f.tell()
                    d = pickle.load(f)
                    if d["credtype"] == "mysql":
                        d["user"] = "root"
                        d["pass"] = ""
                        f.seek(pos)
                        pickle.dump(d, f)
            except EOFError:
                pass
        return None, None


if len(sys.argv) == 1:
    getcreds()
    bruh()
    sys.exit()
else:
    if sys.argv[1] == "dumpsample":
        getcreds()
        databaseinit()
        subprocess.call(
            f"mysql -u root --password=root -D labyrinth < {os.path.abspath('dbdump.sql')}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    elif sys.argv[1] == "initsql":
        user = input("Enter MySQL username: ")
        password = input("Enter MySQL password: ")
        with open("credentials.pickle", "rb+") as f:
            try:
                while True:
                    pos = f.tell()
                    d = pickle.load(f)
                    if d["credtype"] == "mysql":
                        d["user"] = user
                        d["pass"] = password
                        f.seek(pos)
                        pickle.dump(d, f)
            except EOFError:
                pass
        print("Successfully set.")
