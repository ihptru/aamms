#!/usr/bin/python3
## @file Armagetronad.py
 # @brief Functions for Armagetron Advanced server scripting
 # @details This file contains some usefull functions for %Armagetronad server scripting.

import Messages
import sys
import threading
from datetime import datetime
import re
import LadderLogHandlers
import Global
import time

## @brief Executes a command
 # @details Send a command to the server. You only have to replace this function if you
 #          don't want to print commands to stdout.
 # @param command The command to send
def SendCommand(command):
	command=command.replace("\n","\\n") # Never allow to execute more than one command.
	print(command)
	sys.stdout.flush()

## @brief Prints a message
 # @details Writes a message to the game
 # @param msg The message to print
def PrintMessage(msg):
	msgs=msg.split("\n")
	for msg in msgs:
		SendCommand("CONSOLE_MESSAGE 0xffffff"+str(msg) )
	sys.stdout.flush()

## @brief Prints a message to a player
 # @param msg The message to print
 # @param player The player to who to print the message
 # @param color The color which to use for the message. Defaults to Messages.PlayerColorCode
def PrintPlayerMessage(player,msg, color=None):
	if color == None:
		color=Messages.PlayerColorCode
	msg=str(msg)
	msgs=msg.split("\n")
	for msg in msgs:
		SendCommand("PLAYER_MESSAGE "+player+" "+color+msg.replace(" ","\\ ").strip() )

## @brief Gets the position and direction of a player's cycle
 # @details Returns the x,y coordinates and xdir and ydir of a specific player's cycle.
 # @param player The player for which to get the position.
 # @return A tuple x,y, xdir, ydir.
def GetPlayerPosition(player):
	gotpos=threading.Condition()
	def getPos(playername, x, y, xdir, ydir, *args):
		if playername!=player:
			return
		global cur_pos
		cur_pos=tuple([round(float(i),2) for i in (x,y,xdir, ydir)] )
		gotpos.acquire()
		gotpos.notify_all()
		gotpos.release()
	if "PLAYER_GRIDPOS" not in LadderLogHandlers.extraHandlers:
		LadderLogHandlers.extraHandlers["PLAYER_GRIDPOS"]=[]	
	gotpos.acquire()
	LadderLogHandlers.extraHandlers["PLAYER_GRIDPOS"].append(getPos)
	SendCommand("GRID_POSITION_INTERVAL 0")
	SendCommand("LADDERLOG_WRITE_PLAYER_GRIDPOS 1")
	gotpos.wait()
	SendCommand("LADDERLOG_WRITE_PLAYER_GRIDPOS 0")
	LadderLogHandlers.extraHandlers["PLAYER_GRIDPOS"].remove(getPos)
	global cur_pos
	pos=cur_pos
	del cur_pos
	return pos

## @brief Get the value of a game setting.
 # @details Reads the serverlog and looks for a line "SETTING is currently set to X"
 # @param setting The name of the setting.
 # @return The value to which the setting is currently set.
 # @note This requires that the script was started with run.py. Otherwise RuntimeError is raised.
def GetSetting(setting):
	if setting in Global.not_a_setting:	
		raise ValueError("Not a setting.")
	if not Global.serverlog:
		raise RuntimeError("Script wasn't started with run.py or Global.serverlog wasn't set.")
	serverlog=open(Global.serverlog)
	serverlog.seek(0,2)
	timeformat="%Y/%m/%d-%H:%M:%S"
	now=datetime.now()
	SendCommand(setting.upper())
	startpattern=r"\[0[^\]]*] "
	pattern1=re.compile(startpattern+setting.upper()+r" is currently set to (?P<value>[^.]*)\.")
	pattern2=re.compile(startpattern+setting.upper()+r" changed from (?P<value>((([^t]|t+[^o])*)(to)*)*)to \.")
	for i in range(10):
		lines="".join(serverlog.readlines() )
		match=pattern1.search(lines)
		if match==None:
			match=pattern2.search(lines)
		if match==None:
			time.sleep(1)
			continue
		break
	else:
		return ""
	value=match.group("value")
	SendCommand(setting.upper()+" "+value)
	return value
