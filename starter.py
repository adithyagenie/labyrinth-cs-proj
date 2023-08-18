#
# Copyright © 2023 adithyagenie
#
# SPDX-License-Identifier: AGPL-3.0-or-later
#

import os
import pickle
import subprocess
import sys

import maze.modules.PlayerBase_func as player
from maze.modules import bruh

user = password = None

"""Gets mysql pass and username"""
if os.path.exists("credentials.pickle"):
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
else:
    print("credentials.pickle file missing. Refer to README to set it up.")
    sys.exit()


def getcreds():
    """Checks mysql creds"""
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
    """Called with no arguments"""
    getcreds()
    try:
        bruh()
    except KeyboardInterrupt:
        pass
    player.sql.close()
    sys.exit()
else:
    if sys.argv[1] == "dumpsample":
        """dumps sample database"""
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
        """Stores mysql creds"""
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
    elif sys.argv[1] == "setup":
        """Set up credentials.pickle"""
        with open("credentials.pickle", "wb") as f:
            print("SETTING UP EMAIL CLIENT\n")
            email = input(
                "Enter your gmail mail-id which sends the emails (abcd@gmail.com): "
            )
            apppass = input(
                "Create an app-specific password for that mail and input it here: "
            )
            pickle.dump({"credtype": "email", "email": email, "pass": apppass}, f)
            print("Email credentials set successfully!\n")

            print("SETTING UP MYSQL CREDENTIALS\n")
            user = input("Enter MySQL username: ")
            password = input("Enter MySQL password: ")
            pickle.dump({"credtype": "mysql", "user": user, "pass": password}, f)
            print("MySQL credentials set successfully!\n")

            print(
                "SETTING UP OXFORD API\nGenerate your Oxford API key from https://developer.oxforddictionaries.com/ \n"
            )
            appid = input("Enter the app_id: ")
            appkey = input("Enter the app_key: ")
            pickle.dump(
                {
                    "credtype": "oxfordapi",
                    "app_id": appid,
                    "app_key": appkey,
                },
                f,
            )
            print("Oxford API key successfully set!\n")
            print("Set up has completed! You can now play the game!")
            sys.exit()
