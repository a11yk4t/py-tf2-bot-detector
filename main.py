"""
If password has changed check for it and update it!!!
Crashes if loading into game or not in game.
Doesn't differentiate between teams (so it tries to kick people it can't)
Figure out how to deal with finding new cheaters (spam, common words)
How to add new cheaters manually efficiently
Central database that doesn't do accusations and stuff only evident stuff
Try detect new joiners instead of scanning constantly :)

"""

from rcon.source import Client
import json, time, os, re, socket

EXEC_TIME = 1
WAIT_TIME = 5

TF2_DIR = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Team Fortress 2\\tf\\"
TF2_CFG_FILE = TF2_DIR + "cfg\\" + "tf2bd.cfg"

playerlist = json.load(open("cheaters.json", encoding="utf-8"))
ipv4_addr = socket.gethostbyname(socket.gethostname())
password = "password"

#
# Checks for TF2BD.CFG and creates/appends the 
# required commands for starting the RCON server.
#
if os.path.isfile(TF2_CFG_FILE):
    with open(TF2_CFG_FILE, "w+") as file:
        lines = file.readlines()
        if not "net_start" in lines:
            file.write("net_start\n")
        if not f"rcon_address {ipv4_addr}" in lines:
            file.write(f"rcon_address {ipv4_addr}\n")
        if not f"rcon_password {password}" in lines:
            file.write(f"rcon_password {password}\n")
        if not "echo tf2-bot-detect.py running!!" in lines:
            file.write("echo tf2-bot-detect.py running!!\n")
else:
    with open(TF2_CFG_FILE, "w") as file:
        file.writelines([
            "net_start\n", f"rcon_address {ipv4_addr}\n",
            f"rcon_password {password}\n", "echo tf2-bot-detect.py running!!\n"
        ])

while True:
    try:
        with Client(ipv4_addr, 27015, passwd="password") as client:
            while True:
                print("Trying to find a cheater...")

                client.run("clear")
                time.sleep(EXEC_TIME)

                client.run("con_logfile", "status.log")
                time.sleep(EXEC_TIME)

                response = client.run("status")
                print(response)
                time.sleep(EXEC_TIME)

                client.run("con_logfile", "\"\"")
                time.sleep(EXEC_TIME)

                try:
                    with open(TF2_DIR + "status.log", encoding="unicode_escape", errors="ignore") as file:
                        lines = file.readlines()

                    players = {}
                    
                    for line in lines:
                        if line.startswith("#  "):
                            
                            line = re.sub("\s\s+" , " ", line)
                            result = re.search(r"(\d+).+(\".*\").+(\[.*\])", line)
                            uid, name, steamid = result.groups()

                            players[steamid] = {"uid":uid, "name":name}

                            known_cheater = playerlist.get(steamid, None)
                            uid  = players[steamid].get("uid")
                            name = players[steamid].get("name")

                            if known_cheater:
                                print(f"[CHEAT] ({uid}) {name}")
                                # client.run("say", f"Yo guys {name} is cheating. Wack yo kick that guy! This is an automated message.")
                                # client.run("callvote", "kick", uid)
                            else:
                                print(f"[SAFE ] ({uid}) {name}")
                    
                    os.remove(TF2_DIR + "status.log")

                except FileNotFoundError:
                    pass
                
                time.sleep(WAIT_TIME)
                os.system("cls")

    except ConnectionRefusedError:
        print("RCON Server is not running on your TF2 client!")
        time.sleep(2)
    
    except KeyboardInterrupt:
        print("Detected CTRL+C, exiting...")
        break