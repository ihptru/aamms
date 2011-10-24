#!/usr/bin/python3
## @file Commands.py
# @brief Commands
# @details This file declares commands

import Armagetronad
import Player
import Messages
import textwrap
import AccessLevel
import Poll
import tools
import Global
import inspect

__save_vars=["disabled","data"]
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
commandvalues=dict()

###################################### COMMAND HELPERS ###################################

def getDescription(command, acl):
    if command not in commands:
        command=getRealCommand(command)
    acl=int(acl)
    paramstr=""
    desc=commandvalues[command][4]
    brief=desc[0]
    params=desc[1]
    ident_param=2
    ident_param_desc=10
    for param in params:
        acl_needed=float("inf")
        if AccessLevel.accessLevelSet(command.lower()+"_param_"+param[0].lower()):
            acl_needed=AccessLevel.getAccessLevel(command.lower()+"_param_"+param[0].lower())
        if not acl_needed>=acl:
            continue
        paramstr=paramstr+"\n"+" "*ident_param
        paramstr=paramstr+"0x0088ff"+param[0]+":"
        paramdesc=textwrap.wrap(param[1], width=80-ident_param_desc)
        paramstr=paramstr+(ident_param_desc-ident_param-len(param[0]))*" "+" 0xffffff"
        paramstr=paramstr+paramdesc[0]
        paramdesc=paramdesc[1:]
        for desc in paramdesc:
            paramstr=paramstr+"\n"+" "+" "*ident_param_desc+" 0xffffff"+desc+"\n"
    if len(paramstr)==0: paramstr="None"
    return brief, paramstr

        

def getDescriptionInit(command, args):
    if command not in commands:
        command=getRealCommand(command)
    comments=inspect.getcomments(commands[command]) 
    params=[]
    brief="Not documented"
    comments="".join([comment.strip()[1:].strip() for comment in comments.splitlines()])
    if not comments.startswith("#"): return brief, params
    else:
        comments=comments[1:].strip()
    for comment in comments.split("@") :
        comment=comment.split(" ")
        if comment[0]=="brief":
            brief=" ".join(comment[1:])
        elif comment[0]=="param" and comment[1] in args:
            paramname=comment[1].strip()
            paramdesc=" ".join(comment[2:])
            params.append((paramname, paramdesc))
    return brief, params

def initCommand(command):
    if command not in commands:
        command=getRealCommand(command)
    global commandvalues
    argsmin, argsmax, defaultvalues, names=0,0,dict(),[]
    commandf=commands[command]
    argspec=inspect.getfullargspec(commandf)
    names=argspec.args[2:]
    if(argspec.varargs): 
        maxargs=float("inf")
        names+=(argspec.varargs, );
    else:
        maxargs=len(argspec.args)-2
    minargs=len(argspec.args)-2
    if argspec.defaults:
        minargs-=len(argspec.defaults)
        defaultvalues={argname:defaultvalue for argname, defaultvalue in zip(reversed(argspec.args), argspec.defaults)}
    desc=getDescriptionInit(command, names)
    commandvalues[command]=minargs, maxargs, defaultvalues, names, desc
    return

## @brief Gets the parameter of a command
# @details Gets the parameter of the given command from the function definition.
# @param command The name of the command
# @return A tuple of (minargcount, maxargcount, defaultvalues, names)
def getArgs(command,acl):
    if command not in commands:
        command=getRealCommand(command)
    minargcount, maxargcount, defaultvalues, names=commandvalues[command][:4]
    allowed=lambda i: not AccessLevel.accessLevelSet(command.lower()+"_param_"+i.lower()) or AccessLevel.isAllowed(command.lower()+"_param_"+i, acl)
    optionalargs=names[minargcount:]
    newnames=[]
    for name in names:
        if not allowed(name):
            if name not in optionalargs:
                minargcount-=1
            elif name in optionalargs and optionalargs.index(name)==len(optionalargs)-1 and maxargcount==float("inf"):
                maxargcount=minargcount+len(optionalargs)
                continue
            maxargcount-=1
        else:
            newnames.append(name)
    return minargcount, maxargcount, defaultvalues, newnames

def init():
    global commands
    for command in commands:
        initCommand(command)

## @brief Checks the usage of a command
# @details Checks if a command could be called with the given parameters.
# @param command The command for which to check the usage.
# @param args The args which to pass to the command
# @return True if it could be called with that parameters, False otherwise.
def checkUsage(command,acl,  *args):
    if command not in commands:
        command=getRealCommand(command)
    minargcount, maxargcount=getArgs(command, acl)[:2]
    if minargcount <= len(args) <= maxargcount:
        return True
    else:
        return False

## @brief Returns all available commands.
# @details Searches this file for commands and return its names.
# @return The command names.
def getCommands():
    return commands.keys()

## @brief Gets the command line ( /command neededparams [optionalparams]
# @details Retuns the command line for the given command.
# @param command The command for which to get the command line.
# @return The command line.
def getCommandLine(command, acl=0):
    if command not in commands:
        command=getRealCommand(command)
    minargcount, maxargcount, defaultvalues, argnames=getArgs(command, acl)[:4]
    neededargs=argnames[:minargcount]
    if not maxargcount==float("inf"):
        optionalargs=argnames[minargcount:maxargcount]
    else:
        optionalargs=argnames[minargcount:]
    optionalargsstr=""
    if len(optionalargs):
        optionalargsstr="["+"][".join(optionalargs)+"]"
    neededargsstr=" ".join(neededargs)
    command=command.strip()
    if neededargsstr.strip()=="":
        neededargsstr=""
    else:
        neededargsstr=" "+neededargsstr
    optionalargsstr=" "+optionalargsstr
    return ("/" + command + neededargsstr + optionalargsstr).strip()

    


## @brief Gets a help message for a command
# @details Returns a help message for the given command
# @param command The command for which to generate the help message.
# @return The help message
def getHelp(command, acl):
    commandstr=getCommandLine(command,acl)
    commanddesc, params=getDescription(command,acl)
    usagestr="0xff0000Usage: "+"0x00ff00"+commandstr+"\n"+"0xff0000Description: "+"0x00ffee"+commanddesc+"\n0xff0000Parameters: "+Messages.PlayerColorCode+params
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
        initCommand(func.__name__)
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

def find_help_topic_applies(func,apply_on=[list],curtopic=None):
    ret=list()
    if not curtopic:
        curtopic=helpTopics
    if type(curtopic)==tuple:
        if tuple in apply_on:
            if func(curtopic):
                ret.extend((curtopic,))
        curtopic=curtopic[1]
    if type(curtopic) in apply_on:
        if func(curtopic):
            ret.extend((curtopic,))
    if type(curtopic)==dict:
        for i in curtopic.values():
            a=find_help_topic_applies(func, apply_on, curtopic=i)
            if a:
                ret.extend(a)
    if not(len(ret)):
        return False
    else:
        return tools.remove_duplicates(ret)

def add_help_group(group, desc):
    register_help("commands "+group, desc, [])
    
def unregister_command(name):
    if not name.lower() in [i.lower() for i in getCommands()]:
        raise RuntimeError("No command "+name+ " to unregister.")
    name=getRealCommand(name)
    command_listing=find_help_topic_applies(lambda x: name in x, apply_on=[list])
    if not command_listing:
        raise RuntimeError("No command "+name+ " to unregister.")
    else:
        command_listing[0].remove(name)
    global commands
    global commandvalues
    del commands[name]
    del commandvalues[name.lower()]

def getRealCommand(x):
    x=x.lower()
    try:
        return [command for command in commands if command.lower()==x][0]
    except:
        raise RuntimeError("No command "+command)

def unregister_package(name):
    command_topics=find_help_topic_applies(lambda x: any((y for y in x if tools.get_package(commands[getRealCommand(y)]).lower()==name.lower())), apply_on=[list])
    if not command_topics:
        return
    for topic in command_topics:
        for command in [i for i in topic if tools.get_package(commands[getRealCommand(i)]).lower()==name.lower()]:
            unregister_command(command)
        
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
#Empty line NEEDED

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
        Armagetronad.PrintPlayerMessage(player, "[Script Exception] SCRIPT COMMAND: Exception: " + e.__class__.__name__+" "+str(e))
        #Armagetronad.PrintPlayerMessage(player, "[Script Exception] At: " + e.__traceback__.tb_frame.f_code.co_filename+": "+str(e.__traceback__.tb_frame.f_back.f_lineno))
        if Global.debug:
            raise e
## @brief Executes the buffer
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

## @brief Empties the buffer
# @details Clears the buffer of the given player
# @param player The player for who to clear the buffer.
def clearBuffer(acl, player):
    if "buffer" in Player.players[player].data:
        del Player.players[player].data["buffer"]
        Armagetronad.PrintPlayerMessage(player,"Buffer cleared.")

## @brief Prints the buffer
# @details Prints the buffer of the given player to the player.
# @param player The player of who to print the buffer and to who to print the buffer.
def printBuffer(acl, player):
    if "buffer" in Player.players[player].data and "\n".join(Player.players[player].data["buffer"]).strip() != "":
        Armagetronad.PrintPlayerMessage(player,"Buffer: \n" + "\n".join(Player.players[player].data["buffer"]) )
    else:
        Armagetronad.PrintPlayerMessage(player,"Buffer: Empty")

## @brief Get help about commands and more.
# @param topics The name of the topic (topic subtopic1 subtopic2 ...) or of the chat command you'd like to get help on.
def info(acl, player, *topics):
    try:
        commandname=" ".join(topics)
        if commandname.startswith("/"): commandname=commandname[1:]
        commandname_real=[i for i in getCommands() if i.lower()==commandname][0]
        Armagetronad.PrintPlayerMessage(player, getHelp(commandname_real,acl) )
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
        Armagetronad.PrintPlayerMessage(player, "0x8888ffTo get help about one of the following topics, use 0xffff00/info "+" ".join(topics)+" <subtopic_name>")
        for topicname, value in curtopic.items() :
            if type(value)==tuple:
                desc=value[0]
            else:
                desc=""
            Armagetronad.PrintPlayerMessage(player, "0x00ff88"+" ".join(topics)+" "+topicname+": 0xffffff"+desc)
    elif type(curtopic)==str:
        Armagetronad.PrintPlayerMessage(player, curtopic)
    elif type(curtopic)==list:
        Armagetronad.PrintPlayerMessage(player, "0x8888ffCommands in topic 0xaaaa00 "+" ".join(topics)+":")
        Armagetronad.PrintPlayerMessage(player, "0x8888ffFor usage details on a command, use /info <command name>")
        for command in curtopic:
            Armagetronad.PrintPlayerMessage(player, "0x00ff88"+getCommandLine(command, acl)+": 0xffffff"+getDescription(command, 0)[0])
    else:
        Armagetronad.PrintPlayerMessage(player, "0xff0000ERROR No topics available.")

## @brief Clear the screen
def clearScreen(acl, player):
    for i in range(30): #@UnusedVariable
        Armagetronad.PrintPlayerMessage(player, "")
    Armagetronad.PrintPlayerMessage(player, "Test")
    
## @brief Set or get the access level that is needed for a specific command.
# @details Calls AccessLevel.setAccessLevel()
# @param acl The accesslevel of the player
# @param player The name of the player
# @param command The command for which to set the access level.
# @param access The minmal access level that a user must have to excute the given command. If not given, print the needed access. 
def acl(acl, player, command, access=None):
    if access is None:
        Armagetronad.PrintPlayerMessage(player, "0x00ff00The minimal access level needed for "+command+" is "+str(AccessLevel.getAccessLevel(command)))
        return
    try:
        access=int(access)
    except:
        return
    AccessLevel.setAccessLevel(command, access)
    Armagetronad.PrintPlayerMessage(player, Messages.AccessLevelChanged.format(command=command, access=access) )
    
## @brief Vote for the current poll
def yes(acl, player):
    if not Poll.current_poll:
        Armagetronad.PrintPlayerMessage(player, Messages.NoActivePoll)
        return
    try:
        Poll.current_poll.SetPlayerVote(player, True)
        Armagetronad.PrintMessage( Messages.PlayerVotedYes.format(player=Player.players[player].name, target=Poll.current_poll.target) )
        Poll.current_poll.CheckResult(only_sure=True)
    except RuntimeError as r:
        if r.args[1]==1:
            Armagetronad.PrintPlayerMessage(player, Messages.PlayerAlreadyVoted)
        elif r.args[1]==2:
            Armagetronad.PrintPlayerMessage(player, Messages.SpecNotAllowed)

## @brief Vote against the current poll
def no(acl, player):
    if not Poll.current_poll:
        Armagetronad.PrintPlayerMessage(player, Messages.NoActivePoll)
        return
    try:
        Poll.current_poll.SetPlayerVote(player, False)
        Armagetronad.PrintMessage( Messages.PlayerVotedNo.format(player=Player.players[player].name, target=Poll.current_poll.target) )
        Poll.current_poll.CheckResult(only_sure=True)
    except RuntimeError as r:
        if r.args[1]==1:
            Armagetronad.PrintPlayerMessage(player, Messages.PlayerAlreadyVoted)
        elif r.args[1]==2:
            Armagetronad.PrintPlayerMessage(player, Messages.SpecNotAllowed)

## @brief Cancel all currently active polls.
def cancel(acl, player):
    if not Poll.current_poll:
        Armagetronad.PrintPlayerMessage(player, Messages.NoActivePoll)
        return
    Poll.Cancel()

## @brief Reload the script.
def reload_script(acl, player):
    raise Global.ReloadException()
    
  
add_help_group("misc", "Other commands")
add_help_group("voting", "Commands for voting")
register_commands(info, clearBuffer, printBuffer,acl, script,reload_script, execBuffer, group="misc")
register_commands(no, yes,cancel,  group="voting")
init()
