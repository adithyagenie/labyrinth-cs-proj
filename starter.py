import os
import pickle
import subprocess
import sys

import maze.modules.PlayerBase_func as player
from maze.modules import bruh

user = password = None

with open("credentials.pickle", "rb") as f:
    try:
        while True:
            d = pickle.load(f)
            if d["credtype"] == "mysql":
                user = d["user"]
                password = d["pass"]
                break
    except:
        user = password = None


def getcreds():
    if user:
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
            except:
                pass
        return None, None


if len(sys.argv) == 1:
    getcreds()
    try:
        bruh()
    except KeyboardInterrupt:
        pass
    player.sql.close()
    sys.exit()
else:
    if sys.argv[1] == "dumpsample":
        getcreds()
        player.databaseinit()
        subprocess.call(
            f"mysql -u {user} --password={password} -D labyrinth < {os.path.abspath('dbdump.sql')}",
            shell=True  # ,
            # stdout=subprocess.DEVNULL,
            # stderr=subprocess.DEVNULL,
        )
        print("Successfully dumped sample data")

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
            except:
                pass
        print("Successfully set.")
