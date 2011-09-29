import Commands
from . import SimpleMode
import Armagetronad
import Messages
import Poll
import LadderLogHandlers
import Player
import AccessLevel
import inspect

locked=False



## @brief Add a mode. 
#  @details Add a new mode.
#  @param name The name of the mode.
#  @param file The file which to include when the mode gets activated.
#  @param lives The lives each player should get in this mode.
#  @param desc The description of the mode.
def addMode(acl, player, name, file, lives, *desc):
    if name.lower() in SimpleMode.modes:
        Armagetronad.PrintPlayerMessage(player, "0xff0000A mode with that name already exists. If you want to edit it, use /editmode")
        return
    SimpleMode.Mode(name.lower(), file=file, lives=lives, desc=" ".join(desc))
    Armagetronad.PrintPlayerMessage(player, "0x00ff00Mode "+name+" added. It's now ready to use :)")
    
## @brief Edit a mode
#  @param modename The name of the mode you'd like to edit.
#  @param what What do you want to change? (name, desc (=description), lives, file)
#  @param value The new value
def editMode(acl, player, modename, what, *value):
    modename=modename.lower()
    what=what.lower()
    modefields={"lives":int, "name":str, "desc":str, "file":str}
    if what not in modefields:
        Armagetronad.PrintPlayerMessage(player, "Modes do not have a setting called "+ what)
        return
    if modename not in SimpleMode.modes:
        Armagetronad.PrintPlayerMessage(player, Messages.ModeNotExist.format(mode=modename))
        return
    value=" ".join(value)
    try:
        if len(value.strip()):
            setattr(SimpleMode.modes[modename], what, modefields[what](value) )
            Armagetronad.PrintPlayerMessage(player, "0x00ff00"+modename+": "+what+" changed to "+str(value))
        else:
            Armagetronad.PrintPlayerMessage(player, getattr(SimpleMode.modes[modename], what) )
        if what=="name":
            SimpleMode.modes[value]=SimpleMode.modes[modename]
            del SimpleMode.modes[modename]
            SimpleMode.current_mode=SimpleMode.modes[value]
    except ValueError:
        Armagetronad.PrintPlayerMessage(player, "0xff0000Wrong value given!")
## @brief Delete a mode.
#  @param modename The name of the mode which should be deleted.
def deleteMode(acl, player, modename):
    if SimpleMode.current_mode.name==modename: #@UndefinedVariable
        Armagetronad.PrintPlayerMessage("0xff0000Can't delete the current mode. Change it first!")
        return
    del SimpleMode.modes[modename]
## @brief Change the game mode.
#  @param modename The name of the mode to which to set the game mode.
def mode(acl, player, modename, when=None):
    if when!=None:
        type="set"
    if locked:
        Armagetronad.PrintPlayerMessage(player, Messages.ModeLocked)
        return
    if modename.lower() not in SimpleMode.modes:
        Armagetronad.PrintPlayerMessage(player, Messages.ModeNotExist.format(mode=modename))
        return
    if SimpleMode.current_mode:
        if SimpleMode.current_mode.name==modename and type=="vote": #@UndefinedVariable
            Armagetronad.PrintPlayerMessage(player, Messages.ModeAlreadyPlaying)
            return

    def removeActivateMethods(l, name="activate", cls=SimpleMode.Mode):
        ret=[]
        for i in l:
            if not inspect.ismethod(i):
                ret.append(i)
                continue
            if not (i.__name__==name and i.__self__.__class__==cls):
                ret.append(i)
        return ret

    def activator(w="roundend"):
        w=w.lower()
        if w=="now":
            SimpleMode.modes[modename.lower()].activate(kill=True)
        elif w in ("roundend","matchend"):
            w=w.capitalize()
            handler_list=getattr(LadderLogHandlers, "at"+w)
            handler_list=removeActivateMethods(handler_list)
            handler_list.append(SimpleMode.modes[modename.lower()].activate) #UndefiniedVariable
            setattr(LadderLogHandlers, "at"+w, handler_list)
        
    if type=="vote":
        try:
            target="Change mode to '"+modename+"'"
            Poll.Add(target, activator, player)
            Poll.current_poll.SetPlayerVote(player, True)
            Armagetronad.PrintMessage(Messages.PollAdded.format(target=target, player=Player.players[player].name))
            Poll.current_poll.CheckResult(only_sure=True)
        except RuntimeError as r:
            if r.args[1]==1:
                Armagetronad.PrintPlayerMessage(player, Messages.PollAlreadyActive)
            elif r.args[1]==2:
                Armagetronad.PrintPlayerMessage(player, Messages.SpecNotAllowed)
                Poll.Cancel()
            return
    elif type=="set":
        if not AccessLevel.isAllowed("mode_set", acl):
            Armagetronad.PrintPlayerMessage(player, "0xff0000You're not allowed to do that. ")
            return
        when=when.lower()
        access_name="mode_set_"+when
        if AccessLevel.accessLevelSet(access_name) and not AccessLevel.isAllowed(access_name, acl):
            Armagetronad.PrintPlayerMessage(player, "0xff0000You're not allowed to do that. ")
            return
        activator(when)
        if when=="roundend":
            Armagetronad.PrintMessage(Messages.NextRoundMode.format(mode=modename.lower(), player=Player.players[player].name))
        elif when=="matchend":
            Armagetronad.PrintMessage(Messages.NextMatchMode.format(mode=modename.lower(), player=Player.players[player].name))
## @brief List available modes.
def modes(acl, player):
    Armagetronad.PrintPlayerMessage(player, "0x8888ffAvailable Modes on this server:")
    for m in SimpleMode.modes.values():
        Armagetronad.PrintPlayerMessage(player, "    0x88ff44"+m.name+": 0x888800"+m.desc)

## @brief Lock the current mode.
def lockMode(acl, player):
    global locked
    locked=True
    Armagetronad.PrintPlayerMessage(player, "0xff0000Mode locked.")
## @brief Unlock the current mode.
def unlockMode(acl, player):
    global locked
    locked=False
    Armagetronad.PrintPlayerMessage(player, "0x00ff88Mode unlocked.")



Commands.add_help_group("modes", "Commands about modes (edit, add, ...)")
Commands.register_commands(addMode,editMode, deleteMode, lockMode, unlockMode, group="modes")
Commands.register_commands(mode, modes, group="voting")
