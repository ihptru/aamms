import Commands

## @brief Parses a map file and returns respoints.
#  @details Takes a map file for Armagetron Advanced and extracts the respawn points.
#           This is needed for lives because if we don't parse map files, you'd need to
#           list each respoint for each map.
# @param map The map file which to parse.
def ParseRespoints(map):
    pass

## @brief Parses Zones of a Map into Zone objects.
#  @details Takes an armagetron advanced map and returns a list of Zone objects for each
#           Zone definied in the map.
#  @param map The map file
#  @return List of Zone objects.
def ParseZones(map):
    pass

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