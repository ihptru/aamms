#!/usr/bin/env python3
## @file Player.py
# @package Player
# @brief Functions and classes for player management.
# @details This file contains functions and classes that used for player management.

import logging
import Team
import Event
import Armagetronad
import copy

if "players" not in dir():
    ## @brief This variable is used to store the players.
    # @details This variable is a dictionary of players where the ladder name of the player
    #          is the key.
    players=dict()

## @brief Adds a new Player
# @details Use this function to add a new player.
# @param lname The name used on the ladder for the player
# @param name The displayed name of the player
# @param ip The ip of the player
# @exception RuntimeError Raised if a player with the same ladder na,e already exists.
# @note The player is stored in \link Player.players\endlink
# @note This triggers the event "Player added"
def Add(lname,name,ip):
    if lname in players:
        print(players[lname] )
        raise RuntimeError("Player „"+lname+"“ already exists.")
    players[lname]=Player(lname,name,ip)

## @brief Gets a bots
# @details Returns all players that has is_human set to false.
# @return The list of bot names
def getBots():
    bots=[]
    for k,p in players.items():
        if p.is_human==False:
            bots.append(k)
    return bots

## @brief Handles player rename event
# @details This function updates the player list. It's called by player rename event.
# @param oldname The old ladder name of the player
# @param newname The new ladder name of the player
def UpdatePlayer(oldname,newname):
    global log
    if oldname not in players:
        log.error("Player „"+oldname+"“ should be renamed to „"+newname+"“ , but it doesn't exist. Adding it.")
        Add(newname,newname,"127.0.0.1")
        return
    #team=players[oldname].getTeam() #### The team code is buggy. In case players
    #if team != None:                #### rename only at roundend when ONLINE_PLAYER
    #                                #### is written to ladderlog too we could just skip it
    #                                #### and set the team to None (leave the current team.)
    #    pos=Team.teams[team].getPlayerPosition(oldname)
    #team=players[oldname].getTeam()
    players[oldname].leaveTeam(True)
    players[newname]=players[oldname]
    #try:
    #    players[newname].joinTeam(team,quiet=True) ### 
    #    if team != None:
    #        Team.teams[team].shufflePlayer(newname,pos)
    #except:
    #        pass
    del players[oldname]

## @brief Removes a player
# @details This function removes the given player from the \link Player.players\endlink list.
# @param name The ladder name of the player to remove
# @exception RuntimeError Raised if the player doesn't exist.'
# @note This triggers the event "Player removed"
def Remove(name):
    if name not in players:
        raise RuntimeError("Trying to remove player „"+name+"“, but it doesn't exist.")
    del players[name]

## @cond
#logging
logging.getLogger("PlayerModule").addHandler(logging.NullHandler() )
log=logging.getLogger("PlayerModule")
## @endcond



## @class Player.Player
# @brief Class for a player
# @details This class represents an player.
class Player:
	## @property __ladder_name
	 # @brief The name of the player on the ladder
	 # @details This variable is set to the escaped name or login of the player. It's
	 #          used to indentify the player.
	 # @private

	## @property name
	 # @brief The name of the player
	 # @details The full name of the player as it's used in the game

	## @property ip
	 # @brief The player's ip
	 # @details The ip of the player. Used for votes.

	## @property __lives
	 # @brief Remaining lives
	 # @details The remaining lives of the player. 0 if the player is death.

	## @property __old_ladder_name
	 # @brief The old ladder name
	 # @details This variable is set to the in game ladder name.

	## @property __team
	 # @brief The name of the team in which the player is in.
	 # @details The name of the player's team. None if the player is spectating, or
	 #          AI if the player is in the AI team.

	## @property __logged_in
	 # @brief If the player is logged in?
	 # @details True if the player is logged in, False if not.

	## @property ping
	 # @brief The ping of the player
	 # @details The current ping of the player.
	 # @note Currently there's no use for the ping of the player, but it may be used
	 #       in future.

	## @property __old_name
	 # @brief The old name
	 # @details This variable is set to the currently in the game used name.

	## @property color
	 # @brief The color of the player
	 # @details A tuple of the color of the player(r, g, b). Each value is between 0 and 15

	## @property is_human
	 # @brief Is the player human?
	 # @details True is yes, otherwise False.

	## @property data
	 # @brief Store data assigned with the player
	 # @details Used to store additional data assigned with the player.

	## @cond
	__slots__=("__ladder_name","__old_ladder_name","name","ip","__lives","__team",
	           "__logged_in","ping","__old_name","color","is_human","data")
	## @endcond

	## @brief Init function
	 # @details Inits a new Player and adds the properties to it.
	 # @param ladder_name \copybrief __ladder_name
	 # @param name \copybrief name
	 # @param ip \copybrief ip
	def __init__(self, ladder_name, name, ip):
		self.__ladder_name=ladder_name
		self.name=name
		self.ip=ip
		self.__lives=1
		self.__team=None
		self.__old_ladder_name=ladder_name
		self.__logged_in=False
		self.ping=0
		self.__old_name=self.name
		self.color=15,0,0
		self.is_human=True
		self.data=dict()

	## @brief Del function
	 # @details Removes the player from his team
	def __del__(self):
		try:
			self.leaveTeam(quiet=True)
		except:
			pass	

	## @brief Sets the team of the player
	 # @details This function lets the player join the given team
	 # @param teamname The escaped name of the team to which to add the player.
	 #                 None if the player is specating. AI if the player is in the AI team.
	 # @param force Create the team if it doesn't exist?
	 # @param quiet If True, don't print info log messages
	 # @exception RuntimeError Raised if the team doesn't exist and force isn't set
	 # @note This also calls Team::addPlayer (adds the player to the team)
	 # @note This triggers the event "Player joined team"
	 # @note If the team name is AI, is_human is set to False
	def joinTeam(self, teamname, force=False, quiet=False):
		if self.__team == teamname and teamname!=None and teamname in Team.teams:
			if self.getLadderName() in Team.teams[teamname].getMembers():
					return
		self.leaveTeam()
		if teamname == None:
			self.__team=None
			return
		if teamname == "ai":
			self.__team="ai"
			self.is_human=False
		else:
			self.is_human=True
		if teamname not in Team.teams:
			if force:
				log.debug("Team „"+teamname+"“ doesn't exist. Creating it.")
				Team.Add(teamname)
			else:
				raise RuntimeError("Team „" + teamname + "“ doesn't exist.")
		Team.teams[teamname].addPlayer(self.__ladder_name)
		events.triggerEvent("Player joined team",self.__ladder_name,teamname)
		if not quiet:
			log.info("Player „" + self.name + "“ joined team „" + Team.teams[teamname].getName()
			         + "“.")
		self.__team=teamname
		if len(Team.teams[teamname].getMembers() ) == 1:
			Team.teams[teamname].color=self.color

	## @brief Lets the player leave the team
	 # @details This function lets the player leave the team.
	 # @param quiet If True, don't print info log messages
	 # @note This also calls Team::removePlayer (removes the player from the team)
	 # @note This triggers the event "Player left team".
	def leaveTeam(self,quiet=False):
		if self.__team == None:
			return
		teamname=Team.teams[self.__team].getName()
		try:
			Team.teams[self.__team].removePlayer(self.__ladder_name)
		except:
			try:
				Team.teams[self.__team].removePlayer(self.__old_ladder_name)
			except:
				pass
		if len(Team.teams[self.__team].getMembers())==0:
			Team.Remove(self.__team)
		events.triggerEvent("Player left team",self.__ladder_name, self.__team)
		if not quiet:
			log.info("Player „"+self.name+"” left team „"+teamname+"“.")
		self.__team=None

	## @brief Set player's lives
	 # @details This sets the player's lives to the given number. A value less or equal
	 #          0 means the player is death.
	 # @param lives The lives
	 # @note If the number of lives is less than 0, 0 is used for lives.
	 # @note Setting the lives to 0 does NOT immenediately kill the player. For that,
	 #       use Player::kill.
	def setLives(self, lives):
		if lives < 0:
			lives=0
		self.__lives=lives

	## @brief This decreases the player's lives counter by 1
	 # @details Call this function when the player crashed.
	 # @return Remaining lives. 0 is the player is death.
	 # @note This triggers the event "Player crashed". If the lives are less or equal 0
	 #       after decreasing them, "Player died" is also triggered.
	def crashed(self):
		self.__lives=self.__lives-1
		if self.__lives<0:
			log.debug("A player is crashed but shouldn't have been alive. Setting lives to 0.")
			self.__lives=0
		events.triggerEvent("Player crashed",self.__ladder_name)
		if self.__lives==0:
			events.triggerEvent("Player died",self.__ladder_name)
		return self.__lives

	## @brief Kills the player.
	 # @details This function kills the player.
	 # @note The lives of the player are set to 0.
	 # @note This triggers the event "Player killed" and "Player died".
	def kill(self):
		Armagetronad.SendCommand("KILL "+self.__old_ladder_name)
		events.triggerEvent("Player killed",self.__ladder_name)
		events.triggerEvent("Player died",self.__ladder_name)
		self.__lives=0
		log.info("Player " + self.__old_ladder_name + " got killed by the script.")

	## @brief Sets the ladder name
	 # @details This function sets the ladder name.
	 # @param name The new ladder name
	 # @note This triggers the event "Player renamed"
	def setLadderName(self, name):
		oldname=self.__ladder_name
		self.__ladder_name=name
		events.triggerEvent("Player renamed",oldname,self.__ladder_name)

	## @brief Respawns the player
	 # @details This function respawns the player at the given position.
	 # @param x The x-coordinate of the position where to respawn
	 # @param y The y-coordinate of the position where to respawn
	 # @param xdir The x direction
	 # @param ydir The y direction
	 # @param force Force position changing(teleporting) ?
	 # @note This sets Player's lives to 0 if they are less 0
	 # @note This triggers the event "Player respawned"
	def respawn(self, x ,y, xdir, ydir, force):
		if self.__lives < 0:
			self.__lives=0
		if force:
			Armagetronad.SendCommand("KILL "+self.__ladder_name)
		Armagetronad.SendCommand("RESPAWN_PLAYER "+str(self.__ladder_name) + " 0 "+str(x)+
		            " "+str(y)+" "+str(xdir)+" "+str(ydir) )
		if force:
			#SendCommand("TELEPORT_PLAYER {0} {1} {2} {3} {4}".format(self.__old_ladder_name,
			#            y,x,xdir,ydir) )
			pass
		events.triggerEvent("Player respawned",self.__ladder_name)

	## @brief Gets ladder name
	 # @details This function gets the ladder name
	 # @return The ladder name
	def getLadderName(self):
		return self.__ladder_name

	## @brief Applies all changes
	 # @details Should be only called at the end of the round, when the player can rename.
	 # @param force Force renaming?
	def applyChanges(self, force=True):
		if self.__old_name != self.name:
			Armagetronad.SendCommand("RENAME "+self.__old_ladder_name+" "+self.name)
			self.__old_name=self.name
			if force:
				Armagetronad.SendCommand("DISALLOW_RENAME_PLAYER "+self.__ladder_name)
			else:
				Armagetronad.SendCommand("ALLOW_RENAME_PLAYER "+self.__ladder_name)
		self.__old_ladder_name=self.__ladder_name

	## @brief Player logged in
	 # @details Sets logged_in to True and ladder_name to the login
	 # @param global_id The login
	 # @note This triggers the event "Player logged in"
	def login(self,global_id):
		self.__logged_in=True
		self.setLadderName(global_id)
		events.triggerEvent("Player logged in",self.__ladder_name)

	## @brief Player logged out
	 # @details Sets logged in to False and ladder_name to the given ladder_name
	 # @param ladder_name The ladder name to use for the player
	 # @note This triggers the event "Player logged out"
	def logout(self,ladder_name):
		self.__logged_in=False
		self.setLadderName(ladder_name)
		events.triggerEvent("Player logged out", self.__ladder_name)

	## @brief Returns the lives of the player
	 # @details Returns the remaining lives of the player
	def getLives(self):
		return self.__lives

	## @brief Returns in-game ladder name
	 # @details This function return the ladder name of the player that is currently used
	 #          in the game.
	 # @return The in-game ladder name
	def getInGameLadderName(self):
		return self.__old_ladder_name

	## @brief Returns in-game name
	 # @details This function returns the name of the player that is currently used
	 #          in the game
	 # @return The in-game name
	def getInGameName(self):
		return self.__old_name

	## @brief Gets the team name
	 # @details Returns the name of the team the player is in.
	 # @return The escaped name of the team or None of the player is spectating.
	def getTeam(self):
		return self.__team

	## @brief Get the login state.
	 # @details Get if the player is logged in or not.
	 # @return True if the player is logged in, False otherwise.
	def isLoggedIn(self):
		return self.__logged_in

## @brief Enables Logging
# @details This function enables logging for all Player classes. For more information see
#          the logging module.
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

##################### TESTS ###################################################
import unittest

## @brief Test the player module
class PlayerModuleTest(unittest.TestCase):
    def setUp(self):
        self.saved_players=players

    def test_adding(self):
        Add("test_adding_laddername","Test Real name", "127.0.0.1")
        self.assertIn("test_adding_laddername", players.keys(), "Adding of a player failed")

    def test_renaming(self):
        Add("test_rename_player","Test rename player", "127.0.0.1")    
        players["test_rename_player"].setLadderName("renamed_player")
        self.assertNotIn("test_rename_player", players.keys(), "Renaming of a player failed: Old player got not removed from player list")
        self.assertIn("renamed_player", players.keys(), "Renaming of a player failed: Player isn't moved to the new position in the player list")
        self.assertEqual(players["renamed_player"].getLadderName(), "renamed_player", "Renaming of a player failed: Laddername isn't changed")
    
    def test_removing(self):
        Add("test_remove_player","Test remove player", "127.0.0.1")
        Remove("test_remove_player")
        self.assertNotIn("test_remove_player", players.keys(), "Removing of a player failed")

    def test_killing(self):
        testPlayer=Player("test_player", "Test player", "127.0.0.1")
        testPlayer.kill()
        self.assertEqual(testPlayer.getLives(), 0, "Killing failed: Player's lives wasn't set to 0")

    def test_crashing(self):
        testPlayer=Player("test_player", "Test player", "127.0.0.1")
        testPlayer.setLives(1)
        testPlayer.crashed()
        self.assertEqual(testPlayer.getLives(), 0, "Crashing failed: Lives wasn't counted down")

    def tearDown(self):
        players=self.saved_players

## @brief Get a test suite
def suite():
    return unittest.defaultTestLoader.loadTestsFromTestCase(PlayerModuleTest)

if __name__=="__main__":
	nullFunction=lambda *args: None
	Armagetronad.SendCommand=nullFunction
	unittest.TextTestRunner(verbosity=2).run(suite() )
