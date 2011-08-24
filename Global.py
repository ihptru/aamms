#!/usr/bin/env python3
## @file Global.py
 # @brief Global functions and variables
 # @details This file contains global functions and variables.

import Player
import Armagetronad
import AccessLevel
import Mode
from time import sleep
import Commands
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
	if Mode.current_mode in Mode.modes:
		Mode.modes[Mode.current_mode].activate(False)

## @brief Update help topics
 # @details Updates help topics for modes and commands
def updateHelpTopics():
	commands=Commands.getCommands()
	modes=Mode.modes.keys()
	cht=list()
	for command in commands:
		cl=Commands.getCommandLine(command)
		cl="0x44ff00"+cl
		cd,cda=Commands.getDescription(command)
		cd="0xdddddd"+cd
		if AccessLevel.isAllowed(command, 15):
			cht.append(cl+": "+cd)
	commandhelp=r"\n".join(cht)
	modehelp=""
	mht=list()
	for mode in modes:
		name=Mode.modes[mode].short_name
		mht.append("0x44ff00"+name+": 0xdddddd"+Mode.modes[mode].name)
	commandhelp=commandhelp.replace(" ",r"\ ")
	modehelp=r"\n".join(mht)
	modehelp=modehelp.replace(" ",r"\ ")
	Armagetronad.SendCommand(r"ADD_HELP_TOPIC extracommands Extra\ commands\ on\ this\ server "+commandhelp)
	Armagetronad.SendCommand(r"ADD_HELP_TOPIC modes Modes\ avaliable\ on\ this\ server "+modehelp)

## @brief Reloads all modules used by this script
 # @details Reloads all modules loaded by the dcript by calling imp.reload(Module) for each Module
def reloadModules():
		for f in glob.glob(os.path.join(os.path.dirname(__file__),"*.py") ):
			f=os.path.basename(f)
			f=f[:-3]
			if f in sys.modules:
				sys.stderr.write("[RELOADING] Module: "+f+"\n")
				imp.reload(sys.modules[f])

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
