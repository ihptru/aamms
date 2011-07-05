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
import Global
import threading
if "disabled" not in dir():
	###################################### VARIABLES #########################################
	## @brief Commands that couldn't be used in a given state.
	 # @details List of commands that couldn't be used in the given state.
	not_in_state={"normal":[], "modeeditor":[]}

	## @brief Commands that can be only used in a given state.
	 # @details List of commands that can be only used in the given state.
	only_in_state={
	          "normal":["yes","no","mode"], 
	          "modeeditor":["saveMode","makeZone","makeRes", "go","stop", "moreSpeed", "lessSpeed", "modeSetting"]
	              }

	## @brief Disabled commands.
	 # @details List of commands that are disabled (means they cannot be used).
	disabled=[]
	
	## @brief State specific data
	 # @details Data that is only need for a specific state.
	data=None

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
	for arg in args[2:]:
		arg=arg.strip()
		arg=arg.replace(" ","")
		if arg.find("=")==-1:
			if arg.startswith("*"):
				arg=arg[1:]
				maxargcount=100000000000000000000 # Make the number as big as you want
				names.append(arg)
				break
			minargcount=minargcount+1
			maxargcount=maxargcount+1
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
		if func_name in globals():
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
	comstart=-1
	while True:
		if lines[currentlineno].strip().startswith("##"):
			comstart=currentlineno
			break
		if not lines[currentlineno].strip().startswith("#"):
			break
		currentlineno=currentlineno-1
	currentlineno=comstart
	while currentlineno>-1:
		if lines[currentlineno].strip()=="":
			currentlineno=currentlineno-1
			continue
		if lines[currentlineno].strip().startswith("##"):
			commentars.append(lines[currentlineno].strip()[2:].strip() ) #Remove the "##"
		if not lines[currentlineno].strip().startswith("#"):
			break
		commentars.append(lines[currentlineno].strip()[1:].strip() ) #Remove the "#"
		currentlineno=currentlineno+1

	params=list()
	commanddesc=""
	print(commentars)
	commentars="\n".join(commentars).split("@")
	for commentaritem in commentars:
		commentaritem=commentaritem.strip()
		if commentaritem.startswith("brief"):
			commentaritem=commentaritem[len("brief"):]
			commanddesc=commentaritem.strip()
			commanddesc=commanddesc.replace("of a player","")
			commanddesc=commanddesc.replace("a player","you")
		elif commentaritem.startswith("param"):
			commentaritem=commentaritem[len("param"):].strip()
			param, desc=commentaritem.split(" ",1)
			if param not in argnames: # Probably internal arg, not needed to show the user.
				continue
			desc=desc.replace("player's ","your")
			desc=desc.replace("the player ","you")
			if not desc.endswith("."):
				desc=desc+"."
			if param in optionalargs and len(defaultvalues)>optionalargs.index(param):
				desc=desc+(" Defaults to \""+str(defaultvalues[optionalargs.index(param)])+"\".")
			desc=textwrap.wrap(desc, 60)			
			if len(param)<7: len_param=len(param)
			if len(param)>=7: len_param=6 
			params.append(param+" "*(7-len_param)+desc[0])		
			for curdescl in desc[1:]:
				params.append(" "*7+curdescl)
	return commanddesc, params
	


## @brief Gets a help message for a command
 # @details Returns a help message for the given command
 # @param command The command for which to generate the help message.
 # @return The help message
def getHelp(command):
	commandstr=getCommandLine(command)
	commanddesc, params=getDescription(command)
	paramstr=("\n    "+"\n    ".join(params) )
	if len(params)==0:
		paramstr="None"
	usagestr="0xff0000Usage: "+"0x00ff00"+commandstr+"\n"+"0xff0000Description: "+"0x00ffee"+commanddesc+"\n0xff0000Parameters: "+Messages.PlayerColorCode+paramstr
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
	Armagetronad.PrintMessage("[Script Command] Started script execution")
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
def execBuffer(acl, player, flush_buffer=False):
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
def clearBuffer(acl, player):
	if "buffer" in Player.players[player].data:
		del Player.players[player].data["buffer"]
		Armagetronad.PrintPlayerMessage(player,"Buffer cleared.")

## @brief Prints the buffer of a player
 # @details Prints the buffer of the given player to the player.
 # @param player The player of who to print the buffer and to who to print the buffer.
def printBuffer(acl, player):
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
 # @param gmode The mode which to activate.
 # @param type Optional How does the mode get activated? Could be set or vote. Set isn't avaliable for normal players.
 # @param when Optional When gets the mode activated? Only affects if type is set. Could be now, roundend or matchend.
def mode(acl, player, gmode, type="vote", when="now"):
	smode=""
	mode=None
	for key, m in Mode.modes.items():
		if m.short_name.lower()==gmode.lower() or m.getEscapedName==gmode.lower():
			mode=key
			smode=m.short_name.lower()
	if mode not in Mode.modes:
		Armagetronad.PrintPlayerMessage(player, Messages.ModeNotExist.format(mode=gmode))
		return
	if(type=="vote"):
		if Vote.current_vote != None:
			Armagetronad.PrintPlayerMessage(player, Messages.VoteAlreadyActive)
			return
		Vote.Add(Mode.modes[mode].short_name, Mode.modes[mode].activate)
		Vote.current_vote.SetPlayerVote(player, True)
		Armagetronad.PrintMessage(Messages.VoteAdded.format(target=smode, player=Player.players[player].name) )
		return
	elif type=="set":
		if when=="now" and AccessLevel.isAllowed("mode_set_now", acl):
			Mode.modes[mode].activate(True)
		elif when=="roundend" and AccessLevel.isAllowed("mode_set_roundend", acl):
			Armagetronad.PrintMessage("0x00ffffMode will change to {0} after this round. ".format(smode) )
			LadderLogHandlers.atRoundend.append(Mode.modes[mode].activate)
		elif when=="matchend" and AccessLevel.isAllowed("mode_set_matchend", acl):
			Armagetronad.PrintMessage("0x00ffffNext match's gamemode changed to {0}.".format(smode) )
			LadderLogHandlers.atMatchend.append(Mode.modes[mode].activate)
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
		Armagetronad.PrintPlayerMessage(player, Messages.NoActiveVote)
		return
	try:
		Vote.current_vote.SetPlayerVote(player, True)
		Armagetronad.PrintMessage(Messages.PlayerVotedYes.format(player=Player.players[player].name, target=Vote.current_vote.target) )
	except RuntimeError:
		Armagetronad.PrintPlayerMessage(player, Messages.PlayerAlreadyVoted)

## @brief Vote against a vote
 # @details Adds the player to the list of no voters
 # @param acl The accesslevel of the player
 # @param player The name of the player
def no(acl, player):
	if not Vote.current_vote:
		Armagetronad.PrintPlayerMessage(player, Messages.NoActiveVote)
		return
	try:
		Vote.current_vote.SetPlayerVote(player, False)
		Armagetronad.PrintMessage(Messages.PlayerVotedNo.format(player=Player.players[player].name, target=Vote.current_vote.target) )
	except RuntimeError:
		Armagetronad.PrintPlayerMessage(player, Messages.PlayerAlreadyVoted)

## @brief Cancel a vote.
 # @details Cancel the current vote if a vote is active.
 # @param acl The accesslevel of the player
 # @param player The name of the player
def cancel(acl, player):
	if Vote.current_vote:
		Armagetronad.PrintMessage(Messages.VoteCancelled.format(target=Vote.current_vote.target) )
		Vote.Cancel()

## @brief Set the access level that is needed for a specific command.
 # @details Calls AccessLevel.setAccessLevel()
 # @param acl The accesslevel of the player
 # @param player The name of the player
 # @param command The command for which to set the access level.#
 # @param access Optional The minmal access level that a user must have to excute the given command.
def acl(acl, player, command, access=0):
	try:
		access=int(access)
	except:
		return
	AccessLevel.setAccessLevel(command, access)
	Armagetronad.PrintPlayerMessage(player, Messages.AccessLevelChanged.format(command=command, access=access) )
	Global.updateHelpTopics()

## @brief Reload the script.
 # @details This command reloads all files of the script.
 # @param acl The accesslevel of the player
 # @param player The name of the player
def reload(acl, player):
	Armagetronad.PrintPlayerMessage(player,  "0xff0000Reloading script ....")
	Global.reloadModules()

## @brief Enter the mode editor.
 # @details This command changes the state to modeeditor.
 # @param acl The accesslevel of the player
 # @param playername The name of the player
def modeEditor(acl, player):
	if Global.state=="modeEditor":
		Armagetronad.PrintPlayerMessage(player, "0xff0000Already in mode editor state!")
	Armagetronad.SendCommand("INCLUDE settings.cfg")
	Armagetronad.SendCommand("SINCLUDE settings_custom.cfg")
	Armagetronad.SendCommand("DEFAULT_KICK_REASON Server\ under\ maintenance.")
	Armagetronad.SendCommand("ALLOW_TEAM_NAME_PLAYER 1")
	Armagetronad.SendCommand("FORTRESS_CONQUEST_TIMEOUT -1")
	Armagetronad.SendCommand("MAX_CLIENTS 1")
	Armagetronad.SendCommand("SP_TEAMS_MAX 1")
	Armagetronad.SendCommand("TEAMS_MAX 1")
	Armagetronad.SendCommand("SP_AUTO_AIS 0")
	Armagetronad.SendCommand("AUTO_AIS 0")
	Armagetronad.SendCommand("SP_NUM_AIS 0")
	Armagetronad.SendCommand("NUM_AIS 0")
	Armagetronad.SendCommand("CYCLE_SPEED_MIN 0")
	Armagetronad.SendCommand("CYCLE_RUBBER 10000000")
	Armagetronad.SendCommand("SP_WALLS_LENGTH 0.000001")
	Armagetronad.SendCommand("CYCLE_SPEED 5")
	Armagetronad.SendCommand("CYCLE_BRAKE -100")
	Armagetronad.SendCommand("CYCLE_BRAKE_DEPLETE 0")
	Armagetronad.SendCommand("CYCLE_SPEED_DECAY_ABOVE 1.5")
	Armagetronad.SendCommand("CYCLE_ACCEL 0")
	Armagetronad.SendCommand("SP_MIN_PLAYERS 0")
	Armagetronad.SendCommand("CYCLE_TURN_SPEED_FACTOR 1")
	Armagetronad.SendCommand("CYCLE_SPEED_DECAY_BELOW 2")
	Armagetronad.SendCommand("FORTRESS_SURVIVE_WIN 0")
	Vote.Cancel()
	Mode.current_mode=None
	Armagetronad.SendCommand("NETWORK_AUTOBAN_FACTOR 0")
	Armagetronad.PrintPlayerMessage("\n"*4)
	Armagetronad.PrintPlayerMessage(player, "0xff0000Kicking other players ...")
	for playero in Player.players.values():
		if playero.ip!=Player.players[player].ip:
			Armagetronad.SendCommand("KICK "+playero.getLadderName() )
		else:
			playero.kill()	
	Armagetronad.SendCommand("NETWORK_AUTOBAN_FACTOR 10")
	Global.state="modeeditor"
	global data
	data=dict()
	data["speed"]=5
	data["mode"]=Mode.Mode("Unsaved")
	data["stopped"]=False
	message="""0x00ffffWelcome to ModeEditor!
ModeEditor was made to help you creating new modes.
Use the /stop, /go, /lessSpeed and /moreSpeed commands to controll the speed of the cycle.
To add a zone or a respawn point at the current position use /makeZone and /makeRes.
If you want to add a zone or respawn point at a specific position, use /stop and then use /tele.
You can use /modeSetting to change settings like name and lives.
At the end use /saveMode to save the mode.
For more informations see /info modeEditor."""
	Armagetronad.PrintMessage(message)
	            

## @brief Go back to normal state.
 # @details Changes the state to normal.
def normal(acl, player):
	Armagetronad.SendCommand("INCLUDE settings.cfg")
	Armagetronad.SendCommand("SINCLUDE settings_custom.cfg")
	Global.reloadPlayerList()
	if Mode.current_mode:
		Mode.current_mode.activate(True)
	for player in Player.players.values():
		player.kill()
	Global.state="normal"
	global data
	data=None

## @brief Stop the cycle.
 # @details Stop the moving cycle.
def stop(acl, player):
	Armagetronad.SendCommand("CYCLE_SPEED_DECAY_ABOVE 10000000000000000000000000")
	Armagetronad.SendCommand("CYCLE_SPEED_DECAY_BELOW 10000000000000000000000000")
	Armagetronad.SendCommand("CYCLE_SPEED 0")
	global data
	data["stoppped"]=True

## @brief Let the cycle move again.
 # @details Sets CYCLE_SPEED to data["speed"]
def go(acl, player):
	global data
	Armagetronad.SendCommand("CYCLE_SPEED_DECAY_ABOVE 1.5")
	Armagetronad.SendCommand("CYCLE_SPEED_DECAY_BELOW 2")
	Armagetronad.SendCommand("CYCLE_SPEED "+str(data["speed"]) )
	data["stopped"]=False

## @brief Incrase or set the speed of the cycle.
 # @param speed If given, the speed is set to this value. Otherwise it will be incrased by 5.
def moreSpeed(acl, player, speed=None):
	global data
	if speed!=None:
		try:
			data["speed"]=float(speed)
		except:
			data["speed"]=float(data["speed"])+5
	else:
		data["speed"]=float(data["speed"])+5
	if not data["stopped"]:
		Armagetronad.SendCommand("CYCLE_SPEED "+str(data["speed"]) )

## @brief Decrase the speed of the cycle.
def lessSpeed(acl, player):
	global data
	data["speed"]=float(data["speed"])-5
	if data["speed"]<0:
		data["speed"]=0
	if not data["stopped"]:
		Armagetronad.SendCommand("CYCLE_SPEED "+str(data["speed"]) )

## @brief Create a zone at the current position of the cycle.
 # @param name The name of the zone.
 # @param type The type of the zone (Win, death, deathTeam, fortress, ....)
 # @param size The radius of the zone.
 # @param grow The zone growth. Negative values will let the zone shrink.
 # @param r Red
 # @param g Green
 # @param b Blue
 # @param team The team for which the zone should get spawned. 
 #             -1 if the zone doesn't belong to any team. 
 #              0 if the zone should be spawned once for every team.
 # @param extrasettings Additional settings for the zone type (like <rubber> for rubber zones)
def makeZone(acl, player, name,type,size, grow="0", team="-1",r=0,g=0,b=15, extrasettings=""):
	if type not in Zone._ZONE_TYPES :
		Armagetronad.PrintMessage("0xff0000Invalid zone type!")
		return
	cur_pos=Armagetronad.GetPlayerPosition(player)[:2]
	global data
	z=Zone.Zone(name=name, radius=float(size), growth=float(grow), type=type, color=(int(r),int(g),int(b)), position=cur_pos)
	z.settings=extrasettings.split(" ")
	try:
		team=int(team)
	except ValueError:
		Armagetronad.PrintMessage("0xff0000Invalid value for argument team!")
		return
	if team==0:
		team=None
	data["mode"].addZone(team, z)
	if team!=-1 or type in ["fortress", "flag", "deathTeam", "ballTeam"]:
		z.teamnames=[Player.players[player].getTeam()]
	z.spawn()
	Armagetronad.PrintMessage("0xffff00Added "+type+" zone at "+"|".join(map(str, cur_pos)))

## @brief Create a respoint at the current position of the cycle.
 # @param team The number of the team for which the respoint should be used. -1 if the respoint should be used for all teams.
def makeRes(acl, player, team=-1):
	try:
		team=int(team)
	except ValueError:
		Armagetronad.PrintMessage("0xff0000Invalid value for argument team!")
		return
	x,y,xdir,ydir=Armagetronad.GetPlayerPosition(player)
	global data
	data["mode"].addRespoint(x,y,xdir,ydir, team)
	Armagetronad.PrintMessage("0xffff00Added respoint at "+str(x)+"|"+str(y)+" for the team with the number "+str(team))

## @brief Set mode settings
 # @param setting one of: name, short_name, settings_file, max_teams, max_team_members, lives.
 # @param value The value to which the setting should be set. If not given, the current value of the settings is printed.
def modeSetting(acl, player, setting, *value):
	if len(value)!=0:
		value=" ".join(value)
	else:
		value=None
	global data
	if setting in ["max_teams","max_team_members","lives", "arena_size"] and value!=None:
		try:
			value=int(value)
		except ValueError:
			Armagetronad.PrintMessage("0xff0000Invalid value!")
			return
	if setting in ["name", "short_name", "settings_file", "max_teams", "max_team_members","lives"]:
		if value!=None:
			setattr(data["mode"], setting, value)
			Armagetronad.PrintMessage("{0} was set to {1}".format(setting, str(value) ) )
		else:
			Armagetronad.PrintMessage("{0} is currently set to {1}".format(setting, str(getattr(data["mode"], setting) ) ) )
	elif setting in ["arena_size"]:
		data["mode"].settings["ARENA_SIZE"]=value
	else:
		Armagetronad.PrintMessage("0xff0000Invalid setting!")
	return

## @brief Save the mode with its current settings.
def saveMode(acl, player):
	global data
	Mode.modes[data["mode"].getEscapedName()]=data["mode"]
	Global.updateHelpTopics()
	Mode.saveModes(modename=data["mode"].getEscapedName())
	Armagetronad.PrintMessage("0x00ff00Saved mode")	
