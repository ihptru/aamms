#!/usr/bin/env python3
## @file Global.py
# @brief Global functions and variables
# @details This file contains global functions and variables.

import Armagetronad
from time import sleep
import imp
import glob
import os.path
import sys

## @brief Call to reload player list.
# @details This will kill all players and reset match score so the script can reload the player list.
def reloadPlayerList():
    Armagetronad.SendCommand("START_NEW_MATCH")
    Armagetronad.SendCommand("CYCLE_RUBBER -1")
    sleep(2)
    Armagetronad.SendCommand("SINCLUDE settings.cfg")
    Armagetronad.SendCommand("SINCLUDE settings_custom.cfg")

## @brief Reloads all modules used by this script
# @details Reloads all modules.
def reloadModules():
    pass

if "state" not in dir():
    ## @brief Current state.
    # @details Possible values are "normal" or "modeeditor".
    state="normal"
    not_a_setting=("CONSOLE_MESSAGE", "CENTER_MESSAGE", "SAY", "QUIT", "EXIT", "SPAWN_ZONE", 
               "COLLAPSE_ZONE", "TELEPORT_PLAYER", "RESPAWN_PLAYER", "KICK", "SUSPEND", "SILENCE"
               "ADD_HELP_TOPIC", "REMOVE_HELP_TOPIC", "PLAYER_MESSAGE", "UNBAN_IP","UNSUSPEND", "UNBAN_USER")
    not_a_setting_prefixes=("SPAWN_","REMOVE")
    loadedExtensions=[]
    supportedCommands=[]
    availableExtensions=[]
    serverlog=None
    datadir=None
    configdir=None
    debug=False
    server_name="Unnamed server"
