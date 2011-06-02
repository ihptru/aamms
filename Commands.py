#!/usr/bin/python3
## @file Commands.py
 # @brief Commands
 # @details This file declares commands

import Armagetronad
import Zone
import Player
import Team
import Mode
import LadderLogHandlers
import Messages
import textwrap
import Vote
import AccessLevel
import re
###################################### COMMAND HELPERS ###################################

## @brief Gets the parameter of a command
 # @details Gets the parameter of the given command from the function definition.
 # @param Command
 # @return A tuple of (minargcount, maxargcount, defaultvalues, names)
def getArgs(command):
	commandf=globals()[command]
	defline=""
	with open(__file__) as f:
		defline=f.readlines()[commandf.__code__.co_firstlineno-1]
	defline=defline[defline.find("(")+1:defline.rfind(")")]
	args=defline.split(",")
	minargcount=0
	maxargcount=0
	names=list()
	optionalvalues=list()
	for arg in args:
		arg=arg.strip()
		arg=arg.replace(" ","")
		if arg=="player" or arg=="acl": #Internal args
			continue
		if arg.find("=")==-1:
			minargcount=minargcount+1
			maxargcount=maxargcount+1
			if arg.startswith("*"):
				arg=arg[1:]
				maxargcount=100000000000000000000 # Make the number as big as you want
			names.append(arg)
		else:
			argname, unused, defaultvalue=arg.partition("=")
			argname=argname.strip()
			defaultvalue=defaultvalue.replace("\"","").replace("'","").strip()
			names.append(argname)
			optionalvalues.append(defaultvalue)
			maxargcount=maxargcount+1
	return minargcount, maxargcount, optionalvalues, names

## @brief Checks the usage of a command
 # @details Checks if a command could be called with the given parameters.
 # @param command The command for which to check the usage.
 # @param args The args which to pass to the command
 # @return True if it could be called with that parameters, False otherwise.
def checkUsage(command, *args):
	if command.startswith("/"):
		command=command[1:]
	commandf=globals()[command]
	minargcount, maxargcount, unused, unused=getArgs(command)
	if minargcount <= len(args) <= maxargcount:
		return True
	else:
		return False

## @brief Returns all avaliable commands.
 # @details Searches this file for commands and return its names.
 # @return The command names.
def getCommands():
	lines=list()
	with open(__file__) as f:
		lines=f.readlines()
	start=lines.index("#START COMMANDS\n")
	lines=lines[start:]
	lines="".join(lines)
	match_func_def=re.compile("def [^(]+\([^)]*\)\s*:")
	func_defs=match_func_def.findall(lines)
	func_names=list()
	for func_def in func_defs:
		func_name=func_def[3:func_def.find("(")].strip()
		func_names.append(func_name)
	return func_names
		

## @brief Gets the command line ( /command neededparams [optionalparams]
 # @details Retuns the command line for the given command.
 # @param command The command for which to get the command line.
 # @return The command line.
def getCommandLine(command):
	if command.startswith("/"):
		command=command[1:] #Remove the slash
	minargcount, maxargcount, defaultvalues, argnames=getArgs(command)
	neededargs=argnames[:minargcount]
	optionalargs=argnames[minargcount:maxargcount]
	optionalargsstr=""
	if len(optionalargs):
		optionalargsstr="["+(" [").join(optionalargs)+"]"*len(optionalargs)
	neededargsstr=" ".join(neededargs)
	command=command.strip()
	if neededargsstr.strip()=="":
		neededargsstr=""
	else:
		neededargsstr=" "+neededargsstr
	optionalargsstr=" "+optionalargsstr
	return ("/" + command + neededargsstr + optionalargsstr).strip()
## @brief Gets the command description including the param description.
 # @details Returns the description for the given command.
 # @param command The command for which to get the description
 # @return Tuple of command description, param description for the given command
def getDescription(command):
	if command.startswith("/"):
		command=command[1:] #Remove the slash
	commandf=globals()[command]
	minargcount, maxargcount, defaultvalues, argnames=getArgs(command)
	neededargs=argnames[:minargcount]
	optionalargs=argnames[minargcount:maxargcount]

	lines=""
	commentars=list()
	currentlineno=0
	with open(__file__) as f:
		lines=f.readlines()
		currentlineno=commandf.__code__.co_firstlineno - 2
	while True:
		if lines[currentlineno].strip()=="":
			currentlineno=currentlineno-1
			continue
		if lines[currentlineno].strip().startswith("##"):
			commentars.append(lines[currentlineno].strip()[2:].strip() ) #Remove the "##"
			break
		if not lines[currentlineno].strip().startswith("#"):
			break
		commentars.append(lines[currentlineno].strip()[1:].strip() ) #Remove the "#"
		currentlineno=currentlineno-1

	params=list()
	commanddesc=""
	for commentaritem in commentars:
		if commentaritem.startswith("@brief"):
			commentaritem=commentaritem[len("@brief"):]
			commanddesc=commentaritem.strip()
			commanddesc=commanddesc.replace("of a player","")
			commanddesc=commanddesc.replace("a player","you")
		elif commentaritem.startswith("@param"):
			commentaritem=commentaritem[len("@param"):].strip()
			param, desc=commentaritem.split(" ",1)
			if param not in argnames: # Probably internal arg, not needed to show the user.
				continue
			desc=desc.replace("player's ","your")
			desc=desc.replace("the player ","you")
			if not desc.endswith("."):
				desc=desc+"."
			if param in optionalargs:
				desc=desc+" Defaults to "+str(defaultvalues[optionalargs.index(param)])+"."
			desc=textwrap.wrap(desc, 60)
			for curdescl in reversed(desc[1:]):
				params.append(" "*7+curdescl)
			params.append(param+" "*(7-len(param))+desc[0])
	return commanddesc, params
	


## @brief Gets a help message for a command
 # @details Returns a help message for the given command
 # @param command The command for which to generate the help message.
 # @return The help message
def getHelp(command):
	commandstr=getCommandLine(command)
	commanddesc, params=getDescription(command)
	paramstr="\n    "+"\n    ".join(reversed(params) )
	if len(params)==0:
		paramstr="None"
	usagestr="Usage: "+commandstr+"\n"+"Description: "+commanddesc+"\nParameters: "+paramstr
	return usagestr



###################################### COMMANDS ##########################################
#START COMMANDS
##Don't remove the comment before this one, it's needed by the script.

## @brief Evaluates the given code
 # @details This function is used for the /script command in the game
 # @param code The code to evaluate.
 # @param player The player who called /script
def script(acl, player, *code):
	code=" ".join(code)
	code.replace("\"","'")
	try:
		exec(code.replace("print(","Armagetronad.PrintPlayerMessage('"+player+"','[Script Command] Output: ' + ") )
		Armagetronad.PrintPlayerMessage(player, "[Script Command] Script execution finished.")
	except Exception as e:
		Armagetronad.PrintPlayerMessage(player, "[Script Command] Exception: " + e.__class__.__name__+" "+str(e))

## @brief Executes the buffer of a player
 # @param player The player who executed this command
 # @param flush_buffer Flush the player's buffer after it was executed?
 # @details Executes the buffer of the given player
def execbuffer(acl, player, flush_buffer=False):
	if "buffer" not in Player.players[player].data:
		Player.players[player].data["buffer"]=[""]
	string="\n".join(Player.players[player].data["buffer"])
	if string.strip().replace("\n","").replace("\t","")=="":
		msg="You don't have any text to exec in your buffer. Use / <text> to add some."
		Armagetronad.PrintPlayerMessage(player,msg)
		return
	script(acl, player, string)
	if flush_buffer:
		del Player.players[player].data["buffer"]

## @brief Empties the buffer of a player
 # @details Clears the buffer of the given player
 # @param player The player for who to clear the buffer.
def clearbuffer(acl, player):
	if "buffer" in Player.players[player].data:
		del Player.players[player].data["buffer"]
		Armagetronad.PrintPlayerMessage(player,"Buffer cleared.")

## @brief Prints the buffer of a player
 # @details Prints the buffer of the given player to the player.
 # @param player The player of who to print the buffer and to who to print the buffer.
def printbuffer(acl, player):
	if "buffer" in Player.players[player].data and "\n".join(Player.players[player].data["buffer"]).strip() != "":
		Armagetronad.PrintPlayerMessage(player,"Buffer: \n" + "\n".join(Player.players[player].data["buffer"]) )
	else:
		Armagetronad.PrintPlayerMessage(player,"Buffer: Empty")

## @brief Teleports a player to the given position
 # @details Teleports the given player to the given position.
 # @param x The x coordinate to which to teleport
 # @param y The y coordinate to which to teleport
 # @param xdir The x direction
 # @param ydir The y direction
def tele(acl, player, x, y, xdir=0, ydir=1):
	Player.players[player].respawn(x,y,xdir,ydir,True)
	Armagetronad.PrintMessage(Messages.PlayerTeleport.format(player=player,x=x,y=y,xdir=xdir, ydir=ydir) )

## @brief Activates a mode.
 # @details This is the /mode command
 # @param player The player who executed this command
 # @param mode The mode which to activate.
 # @param type Optional How does the mode get activated? Could be set or vote. Set isn't avaliable for normal players.
 # @param when Optional When gets the mode activated? Only affects if type set. Could be now, roundend or matchend (currently only now and roundend is supported)
def mode(acl, player, mode, type="vote", when="now"):
	mode=mode.lower()
	if mode not in Mode.modes:
		Armagetronad.PrintPlayerMessage(player, Messages.ModeNotExist.format(mode=mode))
		return
	if(type=="vote"):
		Vote.Add(Mode.modes[mode].name, Mode.modes[mode].activate)
		Armagetronad.PrintMessage(Messages.VoteAdded.format(target=Mode.modes[mode].name, player=Player.players[player].name) )
		return
	elif type=="set":
		if (not AccessLevel.isAllowed("mode_set_now",acl) and when=="now") or (not AccessLevel.isAllowed("mode_set_roundend",acl) and when=="roundend"):
			Armagetronad.PrintPlayerMessage(Player, "You're not allowed to do this.")
		if when=="now":
			Mode.modes[mode].activate(True)
		elif when=="roundend":
			LadderLogHandlers.atRoundend.append(Mode.modes[mode].activate)
		else:
			pass
	else:
		pass

## @brief Vote for a vote
 # @details Adds the player to the list of yes voters
 # @param acl The accesslevel of the player
 # @param player The name of the player
def yes(acl, player):
	if not Vote.current_vote:
		return #TODO: PRINT A MESSAGE
	try:
		Vote.current_vote.SetPlayerVote(player, True)
		Armagetronad.PrintMessage(Messages.PlayerVotedYes.format(player=Player.players[player].name, target=Vote.current_vote.target) )
	except RuntimeError:
		Armagetronad.PrintPlayerMessage(Messages.PlayerAlreadyVoted)

## @brief Vote against a vote
 # @details Adds the player to the list of no voters
 # @param acl The accesslevel of the player
 # @param player The name of the player
def no(acl, player):
	if not Vote.current_vote:
		return #TODO: PRINT A MESSAGE
	try:
		Vote.current_vote.SetPlayerVote(player, False)
		Armagetronad.PrintMessage(Messages.PlayerVotedNo.format(player=Player.players[player].name, target=Vote.current_vote.target) )
	except RuntimeError:
		Armagetronad.PrintPlayerMessage(Messages.PlayerAlreadyVoted)
