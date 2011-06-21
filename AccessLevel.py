#!/usr/bin/python3
## @file AccessLevel.py
 # @brief Access level management
 # @details This file contains functions for access level management.


import logging
if "__accessLevels" not in dir():
	## @brief Access level needed for a specific commands
	 # @details This is an dictionary of the minimum access level needed for a command, where
	 #          the command is the key.
	 # @private
	__accessLevels=dict()
	## @cond
	log=logging.getLogger("AccessLevel")
	log.addHandler(logging.NullHandler() )
	## @endcond

## @brief Checks access level
 # @details Checks if the the given access level high enough to execute the command.
 # @param command The name of the command for which to check the access level
 # @param access The given access level.
def isAllowed(command, access):
	access=int(access)
	if command not in __accessLevels:
		log.warning("No access level for command "+command+" registered. Using 0 as access level.")
		return (access==0)
	return __accessLevels[command]>=access

## @brief Registers or changes an access level
 # @details Sets the minimum required access level for the given command
 # @param command The command for which to change the access level 
 # @param access The access level
def setAccessLevel(command,access):
	if access < -1:
		log.warning("Access level lower than -1. Using -1 as access level.")
		access=-1
	__accessLevels[command]=access
