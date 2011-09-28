#!/usr/bin/python3
## @file AccessLevel.py
# @brief Access level management
# @details This file contains functions for access level management.

import yaml
from os.path import exists
import logging

__save_vars=["log", "__accessLevels"]

## @brief Access level needed for a specific commands
#  @details This is an dictionary of the minimum access level needed for a command, where
#          the command is the key.
#  @private
__accessLevels=dict()
## @cond
log=logging.getLogger("AccessLevel")
log.addHandler(logging.NullHandler() )
## @endcond

## @brief Checks access level
#  @details Checks if the the given access level high enough to execute the command.
#  @param command The name of the command for which to check the access level
#  @param access The given access level.
def isAllowed(command, access):
    access=int(access)
    if command not in __accessLevels:
        log.warning("No access level for command "+command+" registered. Using 0 as access level.")
        return (access<=0)
    return __accessLevels[command]>=access

## @brief Registers or changes an access level
#  @details Sets the minimum required access level for the given command
#  @param command The command for which to change the access level 
#  @param access The access level
def setAccessLevel(command,access):
    __accessLevels[command]=access

## @brief Get the access level needed.
def getAccessLevel(command):
    if command not in __accessLevels:
        return 0
    else:
        return __accessLevels[command]
    
## @brief Save access levels to a file
# @details Saves access levels to a file by using yaml. 
# @param file: The name of the file to which to save access levels. Default is access.yaml
def save(file="access.yaml"):
    with open(file, "w") as f:
        yaml.dump(__accessLevels, f, default_flow_style=False)

## @brief Read access levels from a file.
#  @details Uses yaml to read the access levels from a file into the memory.
#  @param file The name of the file to read from.
#  e@info If the file doesn't exists, it's ignored.
def load(file="access.yaml"):
    global __accessLevels
    if not exists("access.yaml"):
        return
    with open(file) as f:
        __accessLevels=yaml.load(f)
        
def accessLevelSet(command):
    return command in __accessLevels
