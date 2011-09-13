import Commands
from . import SimpleMode
import Armagetronad
import Messages
import Poll
import LadderLogHandlers
import Player

## @brief Add a mode. 
#  @details Add a new mode.
#  @param name The name of the mode.
#  @param file The file which to include when the mode gets activated.
#  @param lives The lives each player should get in this mode.
#  @param desc The description of the mode.
def addMode(acl, player, name, file, lives, *desc):
    SimpleMode.Mode(name, file=file, lives=lives, desc=" ".join(desc))
    Armagetronad.PrintPlayerMessage(player, "0x00ff00Mode added. It's now ready to use :)")
    
## @brief Change the game mode.
#  @param modename The name of the mode to which to set the game mode.
#  @param type     The change type. Possible values are: set, vote
#  @param when     Only if type is set: When is the mode  activated? Matchend, roundend or now. 
def mode(acl, player, modename, type="vote", when="matchend"):
    if modename.lower() not in SimpleMode.modes:
        Armagetronad.PrintPlayerMessage(player, Messages.ModeNotExist.format(mode=modename))
        return
    if type=="vote":
        try:
            target="Change mode to '"+modename+"'"
            Poll.Add(target, SimpleMode.modes[modename.lower()].activate)
            Armagetronad.PrintMessage(Messages.PollAdded.format(target=target, player=Player.players[player].name))
        except RuntimeError:
            Armagetronad.PrintPlayerMessage(player, Messages.PollAlreadyActive)
            return
    elif type=="set":
        when=when.lower()
        if when=="now":
            SimpleMode.modes[modename.lower()].activate()
        elif when=="roundend":
            LadderLogHandlers.atRoundend.append(SimpleMode.modes[modename.lower()].activate)
        elif when=="matchend":
            LadderLogHandlers.atRoundend.append(SimpleMode.modes[modename.lower()].activate)

## @brief List available modes.
def modes(acl, player):
    Armagetronad.PrintPlayerMessage(player, "0x8888ffAvailable Modes on this server:")
    for m in SimpleMode.modes.values():
        Armagetronad.PrintPlayerMessage(player, "    0x88ff44"+m.name+": 0x888800"+m.desc)

Commands.add_help_group("modes", "Commands about modes (change mode, ...)")
Commands.register_commands(addMode, mode, modes, group="modes")
