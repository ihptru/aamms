#!/usr/bin/python3
## @file Commands.py
# @brief Commands
# @details This file declares commands

import Armagetronad
import Zone
import Player
import Mode
import LadderLogHandlers
import Messages
import textwrap
import Poll
import AccessLevel
import re
import Global
import time
if "disabled" not in dir():
    ###################################### VARIABLES #########################################
    ## @brief Commands that couldn't be used in a given state.
    # @details List of commands that couldn't be used in the given state.
    not_in_state={"normal":[], "modeeditor":[]}

    ## @brief Commands that can be only used in a given state.
    # @details List of commands that can be only used in the given state.
    only_in_state={
              "normal":["yes","no","mode"], 
              "modeeditor":["saveMode","makeZone","makeRes", "go","stop", "moreSpeed", "lessSpeed", "modeSetting", "loadMode", "testMode"]
                  }

    ## @brief Disabled commands.
    # @details List of commands that are disabled (means they cannot be used).
    disabled=[]
    
    ## @brief State specific data
    # @details Data that is only need for a specific state.
    data=None

    ## @brief Help topics
    helpTopics= {
                  "about": ("About this script",Messages.About, 20),
                  "commands":("Help about commands", 
                    {
                      "voting":("Commands for voting",["mode", "yes", "no"]),
                      "modeEditor":("Commands used in the ModeEditor",only_in_state["modeeditor"]), 
                      "misc": ("Other Commands", ["script", "execBuffer", "clearBuffer", "printBuffer", "reload", "info"    ])
                    } )
                }

###################################### COMMAND HELPERS ###################################

## @brief Gets the parameter of a command
# @details Gets the parameter of the given command from the function definition.
# @param Command
# @return A tuple of (minargcount, maxargcount, defaultvalues, names)
def getArgs(command):
    commandf=globals()[command]
    with open(commandf.__code__.co_filename) as f:
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
    minargcount, maxargcount, unused, unused=getArgs(command)
    if minargcount <= len(args) <= maxargcount:
        return True
    else:
        return False

## @brief Returns all available commands.
# @details Searches this file for commands and return its names.
# @return The command names.
def getCommands():
    lines=list()
    func_names=list()
    for mod in Global.loadedExtensions + [None]:
        if mod==None:
            filename=__file__
        else:
            filename=mod.__file__
        with open(filename) as f:
            lines=f.readlines()
        try:
            start=lines.index("#START COMMANDS\n")
        except ValueError:
            start=0
        lines=lines[start:]
        lines="".join(lines)
        match_func_def=re.compile("def [^(]+\([^)]*\)\s*:")
        func_defs=match_func_def.findall(lines)
        for func_def in func_defs:
            func_name=func_def[3:func_def.find("(")].strip()
            if func_name in globals():
                func_names.append(func_name)
    return list(func_names)

## @brief Gets the command line ( /command neededparams [optionalparams]
# @details Retuns the command line for the given command.
# @param command The command for which to get the command line.
# @return The command line.
def getCommandLine(command):
    if command.startswith("/"):
        command=command[1:] #Remove the slash
    minargcount, maxargcount, defaultvalues, argnames=getArgs(command) #@UnusedVariable
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
    neededargs=argnames[:minargcount] #@UnusedVariable
    optionalargs=argnames[minargcount:maxargcount]

    commentars=list()
    with open(commandf.__code__.co_filename) as f:
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
            params.append("0xffcc00"+param+":"+" "*(7-len_param)+Messages.PlayerColorCode+desc[0])        
            for curdescl in desc[1:]:
                params.append(" "*8+curdescl)
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

## @brief Register new commands
# @details Register new functions to be used as commands.
# @param *functions Functions to register.
def register_commands(*functions, group=None):
    if group:
        try:
            a=get_help_topic("commands "+group)
        except ValueError:
            import sys
            sys.stderr.write("Test\n")
            return
    for func in functions:
        globals()[func.__name__]=func
        a[1].append(func.__name__)

def get_help_topic(*path):
    global helpTopics
    curtopic=helpTopics
    for i in path:
        if type(i)!=tuple:
            if i in curtopic:
                curtopic=curtopic[i]
            else:
                raise ValueError("Path doesn't exist")
        else:
            if i in curtopic[1]:
                curtopic=curtopic[1][i]
            else:
                raise ValueError("Path doesn't exist")
    return curtopic

def add_help_group(group, desc):
    register_help("commands "+group, desc, []) 
    
                
        
## @brief Register a help topic for commands or other things.
#  @details Add a new help topic.
#  @param name The name of the help topic.
#  @param label The short description of the topic.
#  @param data The data. (List of commands, text, function which to call when accessing the help topic.)
#  @param access Optional The access level which is required to see this help topic (Usefull for data types text and function)
#  @param override Override existing topics?
def register_help(name,label, data, access=None, override=False):
    h=get_help_topic(*name.split()[:-1])
    if type(h)!=tuple:
        return
    if type(h[1]) == dict:
        name=name.split()[-1]
        if name in h[1] and not override:
            return
        if not access:
            h[1][name]=(label, data)
        else:
            h[1][name]=(label, data, access)
    else:
        return
    

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
    def setSettings():
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
    setSettings()
    Poll.Cancel()
    Mode.current_mode=None
    Armagetronad.SendCommand("NETWORK_AUTOBAN_FACTOR 0")
    Armagetronad.PrintPlayerMessage(player, "0xff0000Kicking other players ...")
    Armagetronad.PrintPlayerMessage(player, "\n"*4)
    for playero in Player.players.values():
        if playero.ip!=Player.players[player].ip:
            Armagetronad.SendCommand("KICK "+playero.getLadderName() )
        else:
            playero.kill()    
    Armagetronad.SendCommand("NETWORK_AUTOBAN_FACTOR 10")
    Armagetronad.SendCommand("LADDERLOG_WRITE_ADMIN_COMMAND 1")
    def HandleAdminCommand(player, ip, acl, *command):
        global data
        if(Armagetronad.IsSetting(command[0]) and len(command)>1):
            data["mode"].settings[command[0]]=" ".join(command[1:])
            Armagetronad.PrintMessage("0xff0000"+command[0]+" changed to "+" ".join(command[1:]))
            setSettings()
    LadderLogHandlers.register_handler("ADMIN_COMMAND", HandleAdminCommand)
    Global.state="modeeditor"
    global data
    data=dict()
    data["speed"]=5
    data["mode"]=Mode.Mode("Unsaved")
    data["stopped"]=False
    def PrintMessage():
        message="""0x00ffffWelcome to ModeEditor! 0xffffff
ModeEditor was made to help you creating new modes.
Use the /stop, /go, /lessSpeed, /moreSpeed and brake commands to controll the speed of the cycle.
To add a zone or a respawn point at the current position of your cycle use /makeZone and /makeRes.
If you want to go to a specific position, use /stop and then use /tele.
You can use /modeSetting to change settings like name and lives.
To change game settings like rubber you can use /admin (i.e. /admin CYCLE_RUBBER 5). Your changes will get recorded.
To save the mode use /saveMode to save the mode. 
If you want to go back to normal mode, use /normal."""
        for msg in message.split("\n"):
            Armagetronad.PrintMessage(msg)
            time.sleep(3)
    LadderLogHandlers.atRoundend.append(PrintMessage)
                

## @brief Go back to normal state.
# @details Changes the state to normal.
def normal(acl, player):
    Armagetronad.SendCommand("INCLUDE settings.cfg")
    Armagetronad.SendCommand("SINCLUDE settings_custom.cfg")
    Global.reloadPlayerList()
    if Mode.current_mode:
        Mode.current_mode.activate(True) #@UndefinedVariable (for Eclipse)
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
    #elif setting in ["arena_size"]:
    #    if value:
    #        data["mode"].settings[setting]=value
    #        Armagetronad.SendCommand(setting+str(value));
    else:
        Armagetronad.PrintMessage("0xff0000Invalid setting!")
    return

## @brief Save the mode with its current settings.
def saveMode(acl, player):
    global data
    Mode.modes[data["mode"].getEscapedName()]=data["mode"]
    Mode.saveModes(modename=data["mode"].getEscapedName())
    Armagetronad.PrintMessage("0x00ff00Saved mode")    

## @brief Test the mode.
def testMode():
    global data
    m=Mode.current_mode
    data["mode"].activate()
    Mode.current_mode=m

## @brief Get help about commands and more.
# @param topics The name of the topic (topic subtopic1 subtopic2 ...) or of a chat command.
def info(acl, player, *topics):
    if " ".join(topics) in getCommands():
        Armagetronad.PrintPlayerMessage(player, getHelp(" ".join(topics) ) )
        return
    acl=int(acl)
    def checkAclTopics(topic2):
        if hasattr(topic2,"__call__"):
            topic2=topic2()
        if type(topic2)==tuple:
            if len(topic2)>2:
                acl_needed=topic2[2]
                if acl_needed<acl:
                    return None
            else:
                acl_needed=0
            topic=topic2[1]
        else:
            topic=topic2
        if type(topic)==dict:
            ret=dict()
            for subtopic in topic:
                newtopic=checkAclTopics(topic[subtopic])
                if newtopic!=None:
                    ret[subtopic]=newtopic
        elif type(topic)==list:
            ret=[]
            for command in topic:
                if AccessLevel.isAllowed(command,acl):
                    ret+=[command]
        elif type(topic)==str:
            if acl<=acl_needed: ret=topic
            else:               ret=""
        if len(ret): 
            if type(topic2)==tuple:
                ret=topic2[0:1]+(ret,)+topic2[2:]
            return ret
        else:        
            return None

    curtopic=checkAclTopics(helpTopics)
    for topicname in topics:
        if type(curtopic)==tuple:
            curtopic=curtopic[1]
        if hasattr(curtopic,"__call__"):
            curtopic=curtopic()
        if topicname in curtopic:
            if type(curtopic)==dict:
                curtopic=curtopic[topicname]
            elif type(curtopic)==list:
                curtopic=getHelp(topicname)
        else:
            Armagetronad.PrintPlayerMessage(player, Messages.InfoTopicInvalid.format(topic=" ".join(topics)) )
            return
    if type(curtopic)==tuple:
        topic_desc=curtopic[0] #@UnusedVariable
        curtopic=curtopic[1]
    else:
        topic_desc="" #@UnusedVariable
    if hasattr(curtopic, "__call__"):
        curtopic=curtopic()
    if type(curtopic)==dict:
        Armagetronad.PrintPlayerMessage(player, "0x8888ffThis topic has the following subtopics: ")
        for topicname, value in curtopic.items() :
            if type(value)==tuple:
                desc=value[0]
            else:
                desc=""
            Armagetronad.PrintPlayerMessage(player, "0x00ff88"+" ".join(topics)+" "+topicname+": 0xffffff"+desc)
    elif type(curtopic)==str:
        Armagetronad.PrintPlayerMessage(player, curtopic)
    elif type(curtopic)==list:
        for command in curtopic:
            Armagetronad.PrintPlayerMessage(player, "0x00ff88/"+command+": 0xffffff"+getDescription(command)[0])
    else:
        Armagetronad.PrintPlayerMessage(player, "0xff0000ERROR No topics available.")
        

## @brief Load a mode to edit.
# @param mode The mode to load. For a list of available modes see /info modes.
def loadMode(acl, player, mode):
    global data
    for k,m in Mode.modes.items():
        if k==mode or m.short_name==mode:
            mode=m
            break
    else:
        Armagetronad.PrintMessage(Messages.ModeNotExist.format(mode=mode) )
    data["mode"]=mode
    mode.activate(False)
    Mode.current_mode=None

def clearScreen(acl, player):
    for i in range(30): #@UnusedVariable
        Armagetronad.PrintPlayerMessage(player, "")
    Armagetronad.PrintPlayerMessage(player, "Test")
    
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
  
