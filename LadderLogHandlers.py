#!/usr/bin/python3
## @file LadderLogHandlers.py
 # @brief Handles ladder log commands
 # @details This file contains functions that handles commands from the ladderlog

import Armagetronad
import Commands
import AccessLevel
import Messages
import Player
import logging
import logging.handlers
import Team
import Mode
import Vote

## @brief The logging object
 # @private
 # @details Used for logging by this module
 # @note To enable or disable logging of this module use \link enableLogging\endlink
log=logging.getLogger("LadderModule")
log.addHandler(logging.NullHandler() )

## @brief Round end handlers
 # @details List of functions called after a round ended. Functions are every object that is callable.
 # @note This list is cleared every time after all the functions were executed.
atRoundend=[]

## @brief Is the round started?
 # @details True if yes, False otherwise.
roundStarted=False

## @brief Handles commands
 # @details Every time when a command that isn't handled by the server is entered, this
 #          function will be called.
 # @param command The command
 # @param player The ladder of the player who tried to execute the command
 # @param ip The ip of the player who tried to execute the command
 # @param access The numeric access level of the player who tried to execute the command
def InvalidCommand(command, player, ip, access, *args):
	if not player in Player.players:
		log.error("Player „"+player+"“ doesn't exist.")
		Armagetronad.PrintPlayerMessage(player, Messages.PlayerNotExist, Messages.PlayerColorCode)
		return
	command=command[1:]
	if command.strip()=="":
		if "buffer" in Player.players[player].data:
			Player.players[player].data["buffer"].append(" ".join(args) )
		else:
			Player.players[player].data["buffer"]=[" ".join(args)]
		Armagetronad.PrintPlayerMessage(player," ".join(args) )
		return
	# get start of commands in file
	lines=list()
	start=0
	with open(Commands.__file__) as f:
		lines=f.readlines()
	try:
		start=lines.index("#START COMMANDS")
	except ValueError:
		start=0
	del lines

	if not hasattr(Commands, command) or getattr(Commands, command).__code__.co_firstlineno<start:
		Armagetronad.PrintPlayerMessage(player, Messages.CommandNotFound.format(command=command) )
		return
	if not AccessLevel.isAllowed(command,access):
		Armagetronad.PrintPlayerMessage(player, Messages.NotAllowed.format(command=command) )
		return
	if not Commands.checkUsage(command, *args):
		Armagetronad.PrintPlayerMessage(player, Commands.getHelp(command))
		return
	args=(access,player) + args
	try:
		getattr(Commands,command)(*args)
	except Exception as e:
		log.error("The command handler for the command /{0} raised an exception.".format(command) )
		raise e

## @brief Handles player joined
 # @details Every time when a player joins the game this function is called.
 # @param lname The name as it's used on the ladder of the player
 # @param ip The ip of the player
 # @param name The name as it's displayed in the game
def PlayerEntered(lname,ip,*name):
	name=" ".join(name)
	log.info("Player {0} entered the server.".format(name) )
	Player.Add(lname,name,ip)

## @brief Handles player renamed
 # @details Every time when a player renames this function is called.
 # @warning This function is only called at round end.
 # @param oldlname The old ladder name of the player who renamed.
 # @param newlname The new ladder name of the player who renamed.
 # @param ip The ip of the player who renamed.
 # @param logged_in If the player is logged in, this is True, otherwise False.
 # @param name The new screen name of the player.
def PlayerRenamed(oldlname,newlname, ip, logged_in, *name):
	name=" ".join(name)
	if not oldlname in Player.players:
		log.warning("„{0}“ renamed but script doesn't know him. Adding him.".format(name) )
		Player.Add(oldlname,name,ip)
	Player.players[oldlname].name=name
	Player.players[oldlname].ip=ip
	if logged_in=="1":
		log.info("Player {0} logged in as {1}".format(oldlname,newlname) )
		Player.players[oldlname].login(newlname)
	else:
		log.info("Player {0} renamed to {1}".format(oldlname,newlname) )
		Player.players[oldlname].logout(newlname)
	Player.players[newlname].applyChanges(False)

## @brief Handles player left
 # @details Every time a player left the game, this function is called.
 # @param lname The ladder name of the player who left.
 # @param ip The ip of the player who left.
def PlayerLeft(lname, ip):
	if not lname in Player.players:
		log.warning("„{0} left the game but the script doesn't know him. Ignoring.".format(lname) )
		return
	log.info("Player {0} left the server.".format(lname) )
	Player.Remove(lname)

## @brief Handle online player
 # @details For each online player this function is called.
 # @param lname The ladder name of the player
 # @param red The red piece of the color
 # @param green The green piece of the color
 # @param blue The blue piece of the color
 # @param ping the ping of the player
 # @param teamname The team name of the player
def OnlinePlayer(lname, red, green, blue, ping, teamname=None):
	if not lname in Player.players:
		log.warning("Player „"+lname+"“ doesn't exist in OnlinePlayer. Ignoring.")
		return
	if not teamname in Team.teams and teamname != None:
		Team.Add(teamname.replace("_"," ").capitalize() )
	Player.players[lname].color=red,green,blue
	Player.players[lname].joinTeam(teamname)
	Player.players[lname].ping=ping

## @brief Handles new round
 # @details Every time a new round starts this function is called.
 # @param date The day when the new round is started
 # @param time The time when the new round is started.
 # @param timezone The timezone of the server.
def NewRound(date, time, timezone):
	global roundStarted
	global atRoundend
	roundStarted=False
	log.info("New round started -----------------------------")
	# Flush bot list (NEEDED because no PlayerLeft is called for bots)
	bots=Player.getBots()
	for bot in bots:
		Player.Remove(bot)
	# Handle roundend actions
	for func in atRoundend:
		try:
			func()
		except Exception as e:
			log.error("Could not execute round end handler "+str(func)+": "+str(e.__class__.__name__) )
	atRoundend=list() # Flush list
	# Votes
	if Vote.current_vote != None:
		if Vote.current_vote.aliveRounds==0:
			Vote.current_vote.CheckResult()
		else:
			Armagetronad.PrintMessage(Messages.VoteInProgress.format(target=Vote.current_vote.target, expire=Vote.current_vote.aliveRounds) )
			Vote.current_vote.aliveRounds=Vote.current_vote.aliveRounds-1

	Armagetronad.SendCommand("LADDERLOG_WRITE_GAME_TIME 1")
	roundStarted=True

## @brief Handles cycle created
 # @details For each cycle which is created, this function is called.
 # @param lname The ladder name of the player who is the owner of this cycle.
 # @param x The x-coordinate where the cycle is created.
 # @param y The y-coordinate where the cycle is created.
 # @param xdir The x direction
 # @param ydir The y direction
def CycleCreated(lname, x, y, xdir, ydir):
	if lname in Player.players:
		return
	Player.Add(lname,lname,"127.0.0.1")
	Player.players[lname].joinTeam("ai")

def GameTime(time):
	if time=="-4" and (Mode.current_mode in Mode.modes):
		Mode.modes[Mode.current_mode].spawnTeams()
	if time=="-2" and (Mode.current_mode in Mode.modes):
		Mode.modes[Mode.current_mode].spawnZones()
		Armagetronad.SendCommand("LADDERLOG_WRITE_GAME_TIME 0")

## @brief Enables logging
 # @details This function enables logging for this module.
 # @param h The handler used for logging
 # @param f The formatter used for logging
 # @param level The logging level
def enableLogging(level=logging.DEBUG, h=None,f=None):
	log.setLevel(level)
	if not h:
		h=logging.StreamHandler()
		h.setLevel(level)
	if not f:
		f=logging.Formatter("[%(name)s] (%(asctime)s) %(levelname)s: %(message)s")
	h.setFormatter(f)
	log.addHandler(h)
