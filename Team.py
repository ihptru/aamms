#!/usr/bin/python3
## @file Team.py
# @package Team
# @brief Functions and classes for team management
# @details This file contains functions and class for team management

import logging
import Armagetronad
import Player
import math
__save_vars=["log", "teams", "max_teams", "max_team_members"]
## @brief The logging object
# @private
# @details Used for logging by this module
# @note To enable or disable logging of this module use \link Team.enableLogging\endlink
log=logging.getLogger("TeamModule")
log.addHandler(logging.NullHandler() )

## @brief All teams
# @details Dictionary of team added with Add(), where the escaped team name
#          is the key.
teams=dict()


## @brief Adds a team
# @details Creates a new team and saves it in the teams list
# @param name The name of the team to create
# @param members Optional members to add to the team.
# @return Escaped name of the added team.
def Add(name, *members):
    t=Team(name,members)
    teams[t.getEscapedName()]=t
    return t.getEscapedName()

## @brief Removes a team
# @details Removes the given team
# @param name The escaped name of the team to remove.
# @exception RuntimeError Raised if the team doesn't exist.
def Remove(name):
    if name not in teams:
        raise RuntimeError("Team {0} doesn't exist.".format(name) )
    del teams[name]

##
## @brief The maximal teams
# @details The maximal number of teams that could be created. A value less or equal 0
#          stands for no limit.
max_teams=-1

## @brief The maximal team members
# @details The number of members that a team can have. A value less or equal 0 stands
#          for no limit.
max_team_members=-1

## @class Team.Team
# @brief A team
# @details This class represents a team. A team can has members, can be killed, renamed, ...
class Team:
    ## @property __members
    # @brief The team members
    # @details The ladder names of the players belong to the team.

    ## @property __name
    # @brief Team name
    # @details The name of the team how it's displayed in the game

    ## @property __id
    # @brief Internal id of the team
    # @details This is the id of the team needed for TEAM_NAME_id and TEAM_RED_id command

    ## @property __ids
    # @brief Set of used ids
    # @details Set of currently used ids
    # @private
    __ids=set()

    ## @property zones
    # @brief Team zones
    # @details The zones belong to the team

    ## @property color
    # @brief The color of the team
    # @details Tuple of the r,g,b value of the color of the team.

    ## @brief Slots
    # @internal
    __slots__=("__members","__name","__id","__ids","zones","color")

    ## @brief Init function (Constructor)
    # @details Inits a new Team and adds properties.
    # @param name The initial team name
    # @param members Initial team members
    # @exception RuntimeError Raised when the team is full (error code 2) or
    #                         teams limit is reached (erro code 1).
    def __init__(self, name,*members):
        if len(Team.__ids) == max_teams and max_teams > 0:
            #raise RuntimeError("Maximal teams limit reached.",1) This should be handled by the server, not by the script.
            pass
        self.__members=list()
        if len(members) != 0:
            self.__members=list(*members)
        self.__name=name
        self.zones=None
        self.color=0,0,1
        id=-1
        # get an unused id
        i=0
        while i<max_teams or max_teams<0:
            if i not in Team.__ids:
                id=i
                break
            i=i+1
        del i
        if id==-1:
            log.error("Bug. Could not find any free id, but teams limit isn't reached.")
            raise AssertionError("Could not find any free id.")
        self.__id=id
        Team.__ids.add(id)

    ## @brief Del function (Destructor)
    # @details Cleans up.
    # @note Do not call this function directly. Use del \<instance\> instead.
    def __del__(self):
        try:
            Team.__ids.remove(self.__id)
            if(self.__name.lower()!="ai"):
                log.debug("Removed id " + str(self.__id) + " from team id's list")
        except AttributeError:
            return
        except KeyError:
            return
        except ValueError:
            return
            

    ## @brief Sets the team name
    # @details This function sets the name of the team.
    # @param name The new team name.
    def setName(self, name):
        oldname=self.__name
        self.__name=name
        teams[self.getEscapedName()]=self
        del teams[oldname]

    ## @brief Applies all changes
    # @details You must call this function to apply changes on the name or
    #          the color of the team
    # @param force Force team name changes by setting TEAM_NAME_AFTER_PLAYER_teamid to 0?
    def applyChanges(self, force=True):
        if force:
            Armagetronad.SendCommand("TEAM_NAME_AFTER_PLAYER_{0} 1".format(self.__id) )
        else:
            Armagetronad.SendCommand("TEAM_NAME_AFTER_PLAYER_{0} 0".format(self.__id) )
        Armagetronad.SendCommand("TEAM_NAME_{0} {1}".format(self.__id, self.__name) )
        r,g,b=self.color
        Armagetronad.SendCommand("TEAM_RED_{0} {1}".format(self.__id,r) )
        Armagetronad.SendCommand("TEAM_GREEN_{0} {1}".format(self.__id,g) )
        Armagetronad.SendCommand("TEAM_BLUE_{0} {1}".format(self.__id,b) )
    ## @brief Adds a player to the team
    # @details This function adds the given player to the member list of the team.
    # @param name The ladder name of the player to add to the team.
    # @exception RuntimeError Raised if the team is full.
    def addPlayer(self, name):
        if len(self.__members)==max_team_members:
            #raise RuntimeError("Team is full.",2) This should be handled by the server, not by the script.
            pass
        if name not in self.__members:
            self.__members.append(str(name) )

    ## @brief Removes a player from the team
    # @details This function removes the given player from the member list of the team.
    # @param name The ladder name of the player to remove from the team.
    # @exception RuntimeError Raised if the player isn't a member of the team.
    def removePlayer(self, name):
        if name not in self.__members:
            raise RuntimeError("Player {0} is not a member of team {1}".format(name,self.__name) )
        self.__members.remove(name)

    ## @brief Kills the whole team
    # @details This function kills all members of the team.
    # @see Player::kill
    def kill(self):
        for playername in self.__members:
            if playername not in Player.players:
                log.warning("Found non-existing player " + playername +
                            " as a member of a team. This might be a Bug.")
                continue
            Player.players[playername].kill()
    ## @brief Crashes the whole team
    # @details This function crashes all members of the team.
    # @see Player::crash
    def crash(self):
        for playername in self.__members:
            if playername not in Player.players:
                log.warning("Found non-existing player " + playername +
                            " as a member of a team. This might be a Bug.")
                continue
            Player.players[playername].crashed()

    ## @brief Respawns the whole team
    # @details This function respawns every player in the team.
    # @param x The x-coordinate where to spawn to player with the position 1 in the team.
    # @param y The y-coordinate where to spawn to player with the position 1 in the team.
    # @param xdir The x direction
    # @param ydir The y direction
    # @param offset The offset for back-moving the players.
    # @param shift The offset for moving the players left or right. Should be greater than 0
    # @param force Force the new position for each player? True if yes.
    # @attention x and y coordinate are NOT relative to xdir and ydir.
    # @see Player::respawn
    def respawn(self, x, y, xdir, ydir, offset, shift, force):
        shift=abs(shift)
        i=0
        log.debug("Spawn team "+self.__name)
        current_shift=0
        hyp=math.sqrt(xdir**2 + ydir**2) # a² + b² = c²
        cosa=ydir/hyp
        sina=xdir/hyp
        rotmat=[[cosa, -sina],
                [sina,  cosa]]
        relative_y=0
        for playername in self.__members:
            if playername not in Player.players:
                log.error("Found non-existing player " + playername +
                            " as a member of a team. This might be a Bug.")
                continue
            factor=1
            if i%2==1:
                factor=-1
            relative_x=current_shift*factor
            rotated_x=rotmat[0][0]*relative_x+rotmat[0][1]*relative_y
            rotated_y=rotmat[1][0]*relative_x+rotmat[1][1]*relative_y
            Player.players[playername].respawn(x+rotated_x,y+rotated_y,xdir,ydir,force)
            log.debug("Player "+playername+" spawned at "+str(x+rotated_x)+"|"+str(y+rotated_y) )
            i=i+1
            if i%2==1:
                current_shift=current_shift+shift
            relative_y=relative_y-i%2*offset

    ## @brief Shuffles an player
    # @details Moves the given player to the given position in the team.
    # @param player The ladder name of the player who to shuffle.
    # @param pos The position to which to shuffle the player. 0 is the 1st position.
    # @exception RuntimeError Raised if the player is not a meber of the team or
    #                         does not exist.
    def shufflePlayer(self, player, pos):
        if player not in self.__members:
            raise RuntimeError("Player {0} is not a member of team {1}".format(player, self.__name) )
        self.__members.remove(player)
        self.__members[pos:pos]=[player]

    ## @brief Gets the position of the player
    # @details Returns the position of the given player in the team.
    # @param name The ladder name of the player from who to get the position.
    # @return The position, where 0 is the 1st position.
    # @exception RuntimeError Raised if the player does not exist in the team.
    def getPlayerPosition(self, name):
        if name not in self.__members:
            raise RuntimeError("Player {0} is not a member of team {1}".format(name, self.__name) )
        return self.__members.index(name)

    ## @brief Gets escaped team name
    # @details Returns the escaped team name. Escaped means: No spaces and uppercase letters.
    # @return The escaped team name
    def getEscapedName(self):
        return self.__name.replace(" ","_").lower()

    ## @brief Returns the name of the team
    # @return The name of the team.
    def getName(self):
        return self.__name

    ## @brief Returns the members of the team
    # @return List of members of the team
    def getMembers(self):
        return self.__members

## @brief Enables logging
# @details This function enables logging for this module.
# @param h The handler used for logging
# @param f The formatter used for logging
# @param level The logging level
def enableLogging(level=logging.DEBUG, h=None,f=None):
    global log
    log.setLevel(level)
    if not h:
        h=logging.StreamHandler()
        h.setLevel(level)
    if not f:
        f=logging.Formatter("[%(name)s] (%(asctime)s) %(levelname)s: %(message)s")
    h.setFormatter(f)
    for handler in log.handlers:
        if type(handler)==type(h):
            log.removeHandler(handler)
    log.addHandler(h)
