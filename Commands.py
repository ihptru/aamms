#!/usr/bin/python3
## @file Commands.py
# @brief Commands
# @details This file declares commands

import Armagetronad
import Player
import Messages
import textwrap
import AccessLevel
import Global
if "disabled" not in dir():
    ###################################### VARIABLES #########################################
    ## @brief Commands that couldn't be used in a given state.
    # @details List of commands that couldn't be used in the given state.
    not_in_state={}
    only_in_state={}


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
                    } )
                }
    commands=dict()

###################################### COMMAND HELPERS ###################################

## @brief Gets the parameter of a command
# @details Gets the parameter of the given command from the function definition.
# @param Command
# @return A tuple of (minargcount, maxargcount, defaultvalues, names)
def getArgs(command):
    global commands
    commandf=commands[command]
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
    #lines=list()
    #func_names=list()
    #for mod in extensions.loadedExtensions + [None]:
    #    if mod==None:
    #        filename=__file__
    #    else:
    #        filename=mod.__file__
    #    with open(filename) as f:
    #        lines=f.readlines()
    #    try:
    #        start=lines.index("#START COMMANDS\n")
    #    except ValueError:
    #        start=0
    #    lines=lines[start:]
    #    lines="".join(lines)
    #    match_func_def=re.compile("def [^(]+\([^)]*\)\s*:")
    #    func_defs=match_func_def.findall(lines)
    #    for func_def in func_defs:
    #        func_name=func_def[3:func_def.find("(")].strip()
    #        if func_name in globals():
    #            func_names.append(func_name)
    return commands.keys()

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
    global commands
    commandf=commands[command]
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
            a=get_help_topic("commands",group)
        except ValueError as v:
            import sys
            sys.stderr.write(str(helpTopics))
            raise v
            return
    global commands
    for func in functions:
        commands[func.__name__]=func
        if func.__name__ not in a[1]:
            a[1].append(func.__name__)

def get_help_topic(*path):
    global helpTopics
    curtopic=helpTopics
    for i in path:
        if type(curtopic)!=tuple:
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
#  @param access Optional The access level which is required to see this help topic (Useful for data types text and function)
#  @param override Override existing topics?
def register_help(name,label, data, access=None, override=False):
    global helpTopics
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


## @brief Get help about commands and more.
# @param topics The name of the topic (topic subtopic1 subtopic2 ...) or of a chat command.
def info(acl, player, *topics):
    try:
        commandname_real=[i for i in getCommands() if i.lower()==" ".join(topics)][0]
        Armagetronad.PrintPlayerMessage(player, getHelp(commandname_real) )
        return
    except IndexError:
        pass
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
        Armagetronad.PrintPlayerMessage(player, "0x8888ffFor usage details, use /info <command name>")
        for command in curtopic:
            Armagetronad.PrintPlayerMessage(player, "0x00ff88/"+command+": 0xffffff"+getDescription(command)[0])
    else:
        Armagetronad.PrintPlayerMessage(player, "0xff0000ERROR No topics available.")

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
  
add_help_group("misc", "Other commands")
register_commands(info, reload, clearBuffer, printBuffer,acl, script, execBuffer, group="misc")