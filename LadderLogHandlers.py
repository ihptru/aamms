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
import Team
import Poll
import Global
from threading import Thread
import threading

__save_vars=["log", "runningCommands"]
## @brief The logging object
# @private
# @details Used for logging by this module
# @note To enable or disable logging of this module use \link enableLogging\endlink
log=logging.getLogger("LadderModule")
log.addHandler(logging.NullHandler() )

## @brief Round|match end handlers
# @details List of functions called after a round|match ended. Functions can be every object that is callable.
# @note This list is cleared every time after all the functions were executed.
atRoundend=[]
atMatchend=[]

extraHandlers=dict()

## @brief Is the round started?
# @details True if yes, False otherwise.
roundStarted=False

## @brief Round number
# @details Current round number starting with 1 for the first round. This number is reseted every time a new match starts.
round=1

runningCommands=[]
## @brief Adds a handler for a ladderlog event.
# @details Adds a custom functions as a handler for a ladderlog event.
# @param event The name of the ladderlog event, in uppercase. Example: INVALID_COMMAND
# @param *functions Function(s) to add as a handler.
def register_handler(event, *functions):
    if event in extraHandlers:
        funcnames=dict()
        for func in extraHandlers[event]:
            funcnames[func.__name__]=func.__module__
        for func in functions:
            if func.__name__ not in funcnames or func.__module__ != funcnames[func.__name__]:
                extraHandlers[event]+=[func]
    else:
        Armagetronad.SendCommand("LADDERLOG_WRITE_"+event+" 1")
        extraHandlers[event]=list(functions)
        
def unregister_handler(event, *functions):
    global extraHandlers
    if event in extraHandlers:
        for func in functions:
            del extraHandlers[event][extraHandlers.index(func)]
        if len(extraHandlers[event])==0:
            Armagetronad.SendCommand("LADDERLOG_WRITE_"+event+" 0")
    else:
        return
    
def unregister_package(name):
    global extraHandlers
    for event in extraHandlers:
        for func in extraHandlers[event]:
            if len(func.__module__.split("."))>1:
                if func.__module__.split(".")[-2].lower()==name.lower():
                    extraHandlers[event].remove(func) 
## @brief Handles commands
# @details Every time when a command that isn't handled by the server is entered, this
#          function will be called.
# @param command The command
# @param player The ladder of the player who tried to execute the command
# @param ip The ip of the player who tried to execute the command
# @param access The numeric access level of the player who tried to execute the command
def InvalidCommand(command, player, ip, access, *args):
    # Check if the command is valid ####
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
    saved_command=command
    command=[realcommand for realcommand in Commands.getCommands() if realcommand.lower()==command]
    if len(command)>1:
        log.warning("More than one function for command "+command[0]+". Chosing 1st one.")
    elif len(command)<1:
        Armagetronad.PrintPlayerMessage(player, Messages.CommandNotFound.format(command=saved_command) )
        return
    command=command[0]
    if command in Commands.disabled:
        Armagetronad.PrintPlayerMessage(player, Messages.DisabledCommand)
        return    
    if Global.state in Commands.not_in_state:
        if command in Commands.not_in_state[Global.state]:
            Armagetronad.PrintPlayerMessage(player, Messages.WrongState.format(command=command) )
            return
    if Global.state in Commands.only_in_state:
        for state, commands in Commands.only_in_state.items():
            if command in commands and Global.state!=state:
                Armagetronad.PrintPlayerMessage(player, Messages.WrongState.format(command=command) )
                return
    if not AccessLevel.isAllowed(command,access):
        Armagetronad.PrintPlayerMessage(player, Messages.NotAllowed.format(command=command) )
        return
    if not Commands.checkUsage(command, access, *args):
        Armagetronad.PrintPlayerMessage(player, Commands.getHelp(command,access))
        return

    # Process command ####
    def ProcessCommand(command, args):
        global runningCommands
        args=(access,player) + args
        try:
            #imp.reload(sys.modules[Commands.commands[command].__module__])
            Commands.commands[command](*args)
        except Exception as e:
            raise e
        try:
            runningCommands.remove(threading.current_thread() )    
        except:
            log.debug("Command thread already removed. Command:"+command)
            pass
    if command=="reload_script": # we need to do this here
        raise Global.ReloadException()
    t=Thread(target=ProcessCommand, args=(command, args), name="HandleCommand"+command.capitalize() )
    t.daemon=True
    global runningCommands
    runningCommands.append(t)
    t.start()

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
        log.warning("„{0}“ renamed but script doesn't know him. Ignoring.".format(name) )
#        Player.Add(oldlname,name,ip)
        return
    Player.players[oldlname].name=name
    Player.players[oldlname].ip=ip
    if newlname==oldlname: return
    if logged_in=="1":
        log.info("Player {0} logged in as {1}".format(Player.players[oldlname].name,newlname) )
        Player.players[oldlname].login(newlname)
    elif Player.players[oldlname].isLoggedIn():
        log.info("Player {0} logged out as {1}".format(Player.players[oldlname].name, Player.players[oldlname].getLadderName()) )
        Player.players[oldlname].logout(newlname)
    else:
        log.info("Player {0} renamed to {1}".format(Player.players[oldlname].name, name) )
        Player.players[oldlname].setLadderName(newlname)
    #Player.players[newlname].applyChanges(False)

## @brief Handles player left
# @details Every time a player left the game, this function is called.
# @param lname The ladder name of the player who left.
# @param ip The ip of the player who left.
def PlayerLeft(lname, ip):
    if not lname in Player.players:
        log.warning("„{0} left the game but the script doesn't know him. Ignoring.".format(lname) )
        return
    log.info("Player {0} left the server.".format(lname) )
    if Poll.current_poll and len([i for i in Player.players if Player.players[i].ip==Player.players[lname]])==1:
        Poll.current_poll.RemovePlayerVote(lname)
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
    allow_team_name_player=1
    try:
        allow_team_name_player=int(Armagetronad.GetSetting("ALLOW_TEAM_NAME_PLAYER") )
    except ValueError:
        try:
            allow_team_name_player=int(Armagetronad.GetSetting("ALLOW_TEAM_NAME_PLAYER") )
        except ValueError:
            pass
    if allow_team_name_player == 0 and teamname!=None:
        teamname=teamname.replace("_", " ").capitalize()
    else:
        teamname=Player.players[lname].name
    if teamname!=None:
        if Player.players[lname].getTeam()==None or Player.players[lname].getTeam().replace(" ","").replace("_","").lower()!=teamname.replace("_","").replace(" ","").lower():
            Player.players[lname].leaveTeam()
            if not teamname in Team.teams and teamname != None:
                log.debug("Teams: "+str(Team.teams) )
                teamname=Team.Add(teamname)
            Player.players[lname].joinTeam(teamname)
        else:
            teamname=Player.players[lname].getTeam()
    elif teamname==None:
        Player.players[lname].leaveTeam()
    if not teamname in Team.teams and teamname != None:
        Team.Add(Player.players[lname].name)
    Player.players[lname].color=red,green,blue
    Player.players[lname].ping=ping

def RoundCommencing(round_num_current, round_num_max):
    global round
    global atRoundend
    global atMatchend
    global roundStarted
    roundStarted=False
    round=int(round_num_current)
    handlers=atRoundend
    if round==1:
        handlers.extend(atMatchend)
        atMatchend=list()
    # Handle roundend|matchend actions
    for func in handlers:
        try:
            func()
        except Exception as e:
            log.error("Could not execute handler "+str(func.__name__)+": "+str(e.__class__.__name__) )
    # Polls
    if Poll.current_poll != None:
        if Poll.current_poll.aliveRounds==0:
            if not Poll.current_poll.CheckResult(only_sure=True):
                Armagetronad.SendCommand("CENTER_MESSAGE "+Messages.PollTimedOut.format(target=Poll.current_poll.target))
                Poll.current_poll=None
        else:
            if not Poll.current_poll.CheckResult(only_sure=True):
                Armagetronad.PrintMessage(Messages.PollInProgress.format(target=Poll.current_poll.target, expire=Poll.current_poll.aliveRounds) )
                Armagetronad.SendCommand("CENTER_MESSAGE "+Messages.PollInProgressCenter) 
                Poll.current_poll.aliveRounds=Poll.current_poll.aliveRounds-1
    atRoundend=list() # Flush list

## @brief Handles new round
# @details Every time a new round starts this function is called.
# @param date The day when the new round is started
# @param time The time when the new round is started.
# @param timezone The timezone of the server.
def NewRound(date, time, timezone):
    global roundStarted
    # Flush bot list (NEEDED because no PlayerLeft is called for bots)
    bots=Player.getBots()
    for bot in bots:
        Player.Remove(bot)
    roundStarted=True
    log.debug("## New round started ##")

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
    if "ai" not in Team.teams:
        Team.Add("AI")
    Player.players[lname].joinTeam("ai", quiet=True)


def Positions(team, *members):  
    try:  
        teams=set([Player.players[p].getTeam() for p in members])
        if len(teams)!=1:
            raise Exception("Got players that are in a different team.")
            return
        team=list(teams)[0]
        for pos, member in enumerate(members):
            Team.teams[team].shufflePlayer(member, pos)
        teamstr=" ".join(Team.teams[team].getMembers() )
        log.info("Team "+team+": "+teamstr)
    except:
        Armagetronad.PrintMessage("Script bugged, but not fatal.")

## @brief Enables logging
# @details This function enables logging for this module.
# @param h The handler used for logging
# @param f The formatter used for logging
# @param level The logging level
def enableLogging(level=logging.DEBUG, h=None,f=None):
    global log
    log.setLevel(level)
    if not h:
        h=logging.StreamHandler()
        h.setLevel(level)
    if not f:
        f=logging.Formatter("[%(name)s] (%(asctime)s) %(levelname)s: %(message)s")
    h.setFormatter(f)
    for handler in log.handlers:
        if type(handler)==type(h):
            log.removeHandler(handler)
    log.addHandler(h)
