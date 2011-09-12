import Commands
from . import SimpleMode
import Armagetronad

## @brief Add a mode. 
#  @details Add a new mode.
#  @param name The name of the mode.
#  @param file The file which to include when the mode gets activated.
#  @param lives The lives each player should get in this mode.
#  @param desc The description of the mode.
def addMode(acl, player, name, file, desc):
    pass
## @brief Change the game mode.
#  @param modename The name of the mode to which to set the game mode. 
def mode(acl, player, modename, type="vote", when="matchend"):
    pass

## @brief List available modes.
def modes(acl, player):
    Armagetronad.PrintPlayerMessage(player, "0x8888ffAvailable Modes on this server:")
    for m in SimpleMode.modes.values():
        print("    0x88ff44"+m.name+": 0x888800"+m.desc)

Commands.add_help_group("modes", "Commands about modes (change mode, ...)")
Commands.register_commands(addMode, mode, modes, group="modes")