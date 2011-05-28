#!/usr/bin/python3
## @file Armagetronad.py
 # @brief Functions for Armagetron Advanced server scripting
 # @details This file contains some usefull functions for %Armagetronad server scripting.

## @brief Executes a command
 # @details Send a command to the server. You only have to replace this function if you
 #          don't want to print commands to stdout.
 # @param command The command to send
def SendCommand(command):
	print(command)

## @brief Prints a message
 # @details Writes a message to the game
 # @param msg The message to print
def PrintMessage(msg):
	SendCommand("CONSOLE_MESSAGE "+str(msg) )

## @brief Prints a message to a player
 # @param msg The message to print
 # @param player The player to who to print the message
 # @param color The color which to use for the message
def PrintPlayerMessage(player,msg, color="0xffffff"):
	msg=str(msg)
	msgs=msg.split("\n")
	for msg in msgs:
		SendCommand("PLAYER_MESSAGE "+player+" "+color+msg.replace(" ","\\ ").strip() )
