import Commands
from . import SimpleMode
import Armagetronad
import Messages
import Poll
import LadderLogHandlers
import Player
import AccessLevel

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
#  @param mode The name of the mode you'd like to edit.
#  @param what What do you want to change? (name, desc (=description), lives, file)
#  @param value The new value
def editMode(acl, player, modename, what, value):
    modename=modename.lower()
    value=" ".join(value)
    if modename not in SimpleMode.modes:
        Armagetronad.PrintPlayerMessage(player, Messages.ModeNotExist.format(mode=modename))
        return
    modefields={"lives":int, "name":str, "desc":str, "file":str}
    what=what.lower()
    if what not in modefields:
        Armagetronad.PrintPlayerMessage(player, "Modes do not have a setting called "+ what)
    try:
        setattr(SimpleMode.modes[modename], what, modefields[what](value) )
        Armagetronad.PrintPlayerMessage(player, "Operation successful")
    except ValueError:
        Armagetronad.PrintPlayerMessage(player, "0xff0000Wrong value given!")
## @brief Change the game mode.
#  @param modename The name of the mode to which to set the game mode.
#  @param type     The change type. Possible values are: set, vote
#  @param when     Only if type is set: When is the mode  activated? Matchend, roundend or now. 
def mode(acl, player, modename, type="vote", when="matchend"):
    if modename.lower() not in SimpleMode.modes:
        Armagetronad.PrintPlayerMessage(player, Messages.ModeNotExist.format(mode=modename))
        return
    if SimpleMode.current_mode:
        if SimpleMode.current_mode.name==modename: #@UndefinedVariable
            Armagetronad.PrintPlayerMessage(player, Messages.ModeAlreadyPlaying)
            return
    if type=="vote":
        try:
            target="Change mode to '"+modename+"'"
            Poll.Add(target, SimpleMode.modes[modename.lower()].activate)
            Poll.current_poll.SetPlayerVote(player, True)
            Armagetronad.PrintMessage(Messages.PollAdded.format(target=target, player=Player.players[player].name))
        except RuntimeError:
            Armagetronad.PrintPlayerMessage(player, Messages.PollAlreadyActive)
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
        if when=="now":
            SimpleMode.modes[modename.lower()].activate()
        elif when=="roundend":
            LadderLogHandlers.atRoundend.append(SimpleMode.modes[modename.lower()].activate)
            Armagetronad.PrintMessage(Messages.NextRoundMode.format(mode=modename.lower()), player=Player.players[player].name)
        elif when=="matchend":
            LadderLogHandlers.atRoundend.append(SimpleMode.modes[modename.lower()].activate)
            Armagetronad.PrintMessage(Messages.NextMatchMode.format(mode=modename.lower(), player=Player.players[player].name))
## @brief List available modes.
def modes(acl, player):
    Armagetronad.PrintPlayerMessage(player, "0x8888ffAvailable Modes on this server:")
    for m in SimpleMode.modes.values():
        Armagetronad.PrintPlayerMessage(player, "    0x88ff44"+m.name+": 0x888800"+m.desc)

Commands.add_help_group("modes", "Commands about modes (change mode, ...)")
Commands.register_commands(addMode,editMode,  mode, modes, group="modes")