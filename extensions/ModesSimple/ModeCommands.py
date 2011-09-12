import Commands

## @brief Add a mode. 
#  @details Add a new mode.
#  @param name The name of the mode.
#  @param file The file which to include when the mode gets activated.
#  @param lives The lives each player should get in this mode.
#  @param desc The description of the mode.
def AddMode(acl, player, name, file, desc):
    pass

Commands.add_help_group("ModeManager", "Commands for managing modes (Add, Edit, Remove)")
Commands.register_commands(AddMode, group="ModeManager")