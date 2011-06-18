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

## @brief Call to reload player list.
 # @details This will kill all players and reset match score so the script can reload the player list.
def reloadPlayerList():
	Armagetronad.SendCommand("START_NEW_MATCH")
	Armagetronad.SendCommand("CYCLE_RUBBER -1")
	sleep(2)
	Armagetronad.SendCommand("CYCLE_RUBBER 1")
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
	Armagetronad.SendCommand(r"ADD_HELP_TOPIC commands_extra Extra\ commands\ on\ this\ server "+commandhelp)
	Armagetronad.SendCommand(r"ADD_HELP_TOPIC modes Modes\ avaliable\ on\ this\ server "+modehelp)
