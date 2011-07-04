#!/usr/bin/python3
## @file Mode.py
 # @brief Classes and functions for mode management
 # @details This file contains classes and functions for mode management
 # @package Mode

import Zone
import copy
import Player
import Team
import random
import Armagetronad
import logging
import logging.handlers
import LadderLogHandlers
import yaml
from glob import glob
import os.path
import os

if "settings_prefix" not in dir():
	## @brief Global settings directory
	 # @details This is used as default for settings_prefix by new modes.
	settings_prefix="MultiModeServer/"

	## @brief The logging object
	 # @private
	 # @details Used for logging by this module
	 # @note To enable or disable logging of this module use \link Team.enableLogging\endlink
	log=logging.getLogger("ModeModule")
	log.addHandler(logging.NullHandler() )

	## @brief Stores all modes
	 # @details This is a dictionary of all avaliable modes, where the name of the mode is the key.
	modes=dict()

	## @brief The current mode
	 # @details The escaped name of the currently active mode.
	current_mode=None

## @brief Adds a new mode
 # @details Adds a mode and stores it in the modes list
 # @param name The name of the mode which to use for the new mode.
 # @param settings_file The settings file which is include when the mode gets activated.
 # @param settings Optional The initial settings for the mode. This can also be changed later.
 # @see Mode.__init__
 # @note If the mode the first mode which is added, it is activated.
def Add(name, settings_file=None, settings=dict() ):
	m=Mode(name, settings_file, **settings)
	modes[m.getEscapedName()]=m
	if len(modes)==1:
		m.activate()
	log.info("Mode "+ name + " added.")

## @brief Deletes the mode
 # @details Deletes the given mode. If the mode was activated, the first mode is activated.
 # @param name The escaped name of the mode to delete.
 # @exception RuntimeError Raised if the mode doesn't exit.
def Remove(name):
	if name not in modes:
		raise RuntimeError
	dname=modes[name].name
	del modes[name]
	if current_mode == name and len(modes)>0:
		modes.values()[0].activate()
	log.info("Mode "+dname+" removed.")

## @brief Saves all modes
 # @details Saves the modes in Mode.modes.
 # @param dir Optional The directory where the mode files should be written.
 # @param ext Optional The file extension which the mode files should have, including the point.
 # @param modename Optional Save only the mode with the escaped name modename. By default all modes are saved.
def saveModes(dir="Modes", ext=".aamode", modename=None):
	global modes
	if not dir.endswith("/"):
		dir=dir+"/"
	if not os.path.exists(dir):
		os.mkdir(dir)
	if modename==None:
		for mode in modes.values():
			f=open(dir+mode.getEscapedName()+ext,"w")
			yaml.dump(mode, f)
	else:
		if modename in modes:
			f=open(dir+modename+ext,"w")
			yaml.dump(modes[modename], f)

## @brief Loads modes
 # @details Loads the modes from a directory.
 # @param dir Optional The directory from which the modes should be loaded.
 # @param ext Optional The file extensions that mode files have, including the point.
def loadModes(dir="Modes", ext=".aamode"):
	if not os.path.exists(dir):
		return
	global modes
	if not dir.endswith("/"):
		dir=dir+"/"
	modefiles=glob(dir+"*"+ext)
	for filename in modefiles:
		f=open(filename, "r")
		m=yaml.load(f)
		modes[m.getEscapedName()]=m
		log.info("Loaded mode "+m.name)
	

## @class Mode.Mode
 # @brief A mode
 # @details This class represents a mode. It stores all information about the mode.
class Mode(yaml.YAMLObject):
	## @property name
	 # @brief The name of the mode
	 # @details A string which contains the name of the mode.

	## @property __zones
	 # @brief The zones of the modes.
	 # @details A list of zones. Each item is a tuple of team and the zone object.
	 #          The team could be None if the zone should be spawned for all teams.
	 #          Otherwise, set team to the number of the team for which the zone
	 #          should be spawned, or -1 if the zone doesn't belong to any team and
	 #          should allways be spawned.

	## @property max_teams
	 # @brief Maximal teams that can be active in this mode.
	 # @details The number of teams the could be active in this mode or 0 for unlimited.

	## @property max_team_members
	 # @brief How much members a team can have maximaly.
	 # @details Number of maximal members per team or 0 for unlimited.

	## @property settings_file
	 # @brief The settings file which to include when the mode gets activated.
	 # @details The path of the file which gets include when the mode is activated, relative
	 #          to settings_prefix

	## @property settings_prefix
	 # @brief The directory under which the settings files are stored.
	 # @details Path to the directory which contains the setting files.
	 # @see settings_file

	## @property __respoints
	 # @brief Respoints of this mode.
	 # @details List of respawn points. Each respawn point is a tuple of team,x,y,xdir and ydir.
	 #          Where x,y are the coordinates, and xdir and ydir are the dirtion.
	 #          If the respoint should be avaliable for all teams, set team to None.
	 #          Else set team to the number of the team for which the respoint should be
	 #          avaliable.

	## @property settings
	 # @brief Additional settings.
	 # @details Dictionary of settings where the key is the name of the setting and the
	 #          value is the value of the setting.

	## @property __restype
	 # @brief How should the respoints be used?
	 # @details Could be random_roundstart, random_allways, toggle_roundstart,
	 #          toggle_allways,toggle_whileround, random_whileround or first.

	## @property __last_respoint
	 # @brief The last used respoint.
	 # @details The number of the last-used respoint for each team.

	## @property lives
	 # @brief How much lives does a player have?
	 # @details Number of lives a player has in this mode.

	## @brief Slots
	 # @details See http://docs.python.org OOP
	 # @internal
	__slots__=("name","__zones","max_teams","max_team_members","settings_file",
	           "__respoints","settings","__restype","__last_respoint","short_name","lives")
	## @brief Yaml settings
	 # @details See http://pyyaml.org/wiki/PyYAMLDocumentation for details to the PyYaml library.
	 # @internal
	 # @cond
	yaml_tag="!mode"
	## @endcond

	## @brief Which variables shouldn't be saved by object serialized?
	 # @details Variables to exclude in __get_state__
	 # @internal
	__not_persistent=("__last_respoint")
 
	## @brief Init function (Constructor)
	 # @details Inits a new Mode object and adds properties to it.
	 # @param name The name of the mode
	 # @param settings_file The settings file which is include when the mode gets activated.
	 # @param settings Additional settings.
	def __init__(self, name, settings_file=None, **settings):
		self.name=name
		self.settings_file=settings_file
		self.settings=settings
		self.__zones=list()
		self.__respoints=list()
		self.max_team_members=-1
		self.max_teams=-1
		self.__restype="toggle_roundstart"
		self.__last_respoint=dict()
		self.short_name=name.replace(" ","_").lower()
		self.lives=1

	## @brief Adds a respoint
	 # @details Adds the given respoint to the internal respoint list.
	 # @param x The x-coordinate of the respoint.
	 # @param y The y-coordinate of the respoint.
	 # @param xdir The x-direction
	 # @param ydir The y-direction
	 # @param team Optional the number of the team for which the respoint should be used.
	 #             If not given, the respoint is used for all teams.
	def addRespoint(self, x, y, xdir, ydir, team=-1):
		if team not in self.__last_respoint:
			self.__last_respoint[team]=0
		self.__respoints.append( (team,x,y,xdir,ydir) )

	## @brief Deletes all respoints
	 # @details Cleans the intern respoint list.
	def deleteRespoints(self):
		self.__respoints=list()

	## @brief Gets respoints.
	 # @details Returns a deepcopy of the intern respoint list.
	 # @return A deepcopy of the repoints.
	def getRespoints(self):
		return copy.deepcopy(self.__respoints)

	## @brief Call this when a player crashed.
	 # @details This function will handle the crash and if the lives of the player arent't
	 #          0, it will respawn the player.
	 # @param player The ladder name of the player who crashed.
	 # @param type The type of the crash("DEATH_FRAG","DEATH_TEAMKILL",...)
	 # @return Has the player been respawned?
	def playerCrashed(self, player, type=None):
		Player.players[player].crashed()
		if Player.players[player].getLives()==0:
			return
		if len(self.__respoints)==0:
			log.warning("No respoints for mode {0} registered.".format(self.name) )
			return False
		# get a repoint
		respoint=None
		i=0
		for team in Team.teams.keys():
			if team==Player.players[player].getTeam():
				break
			i=i+1
		if i==len(Team.teams):
			log.error("Player „{0}“ has an invalid team".format(player) )
			return
		respoint=self.getRespoint("normal",i)
		t,x,y,xdir,ydir=respoint
		Player.players[player].respawn(x,y,xdir,ydir,False)

	## @brief Enables the mode
	 # @details Includes the file given with settings_file and sets all the other settings.
	 # @param kill Kill all players to activate the mode? Default True when round is already started, otherwise False.
	def activate(self, kill=None):
		global settings_prefix
		global current_mode
		if kill == None:
			if LadderLogHandlers.roundStarted:
				kill=True
			else:
				kill=False
		settings_prefix=settings_prefix.rstrip("/")
		Armagetronad.SendCommand("START_NEW_MATCH")
		if self.settings_file != None:
			Armagetronad.SendCommand("INCLUDE {0}/{1}".format(settings_prefix, self.settings_file) )
		Armagetronad.SendCommand("TEAMS_MAX "+str(self.max_teams) )
		Armagetronad.SendCommand("TEAM_MAX_PLAYERS "+str(self.max_team_members) )
		for setting, value in self.settings.items():
			Armagetronad.SendCommand("{0} {1}".format(setting,value) )
		Team.max_teams=self.max_teams
		Team.max_team_members=self.max_team_members
		if kill == True:
			for player in Player.players.values():
				player.kill()
		current_mode=self.getEscapedName()
		log.info("Mode "+current_mode+" activated.")

	## @brief Spawns all players (teams)
	 # @details Spawns all teams by using the respoints.
	def spawnTeams(self):
		i=0
		log.debug("Spawn teams ...")
		for team in Team.teams:
			try:
				respoint=self.__getRespoint("roundstart",i)
				t,x,y,xdir,ydir=respoint
				Team.teams[team].respawn(x,y,xdir,ydir,1,1,True)
			except Exception as e:
				log.error("Could not spawn team {0}: {1}".format(str(team),str(e)) )
			i=i+1

	## @brief Spawns all zones
	 # @details Spawns all zones related to the mode
	def spawnZones(self):
		log.debug("Spawn zones ...")
		for team,zone in self.__zones:
			if team==None:
				for team in Team.teams.values():
					zone.color=team.color
					zone.teamnames=[team.getEscapedName(),]
					zone.spawn()
				return
			elif team == -1:
					zone.spawn()
			else:
				if len(Team.teams)-1 < team-1:
					continue
				zone.teamnames=[list(Team.teams.keys())[team-1]]
				zone.spawn()
	## @brief Gets a respoint
	 # @details Gets a respoint for roundstart or normal for the given team
	 # @param mode The mode which to use (roundstart, normal)
	 # @param team_num the number of the team for which to get a respoint.
	 # @exception RuntimeError Raised if no respoints for the given team exist.
	 # @exception RuntimeError Raised if the type is  unknown
	def __getRespoint(self, mode, team_num):
		team_respoints=[]
		for respoint in self.__respoints:
			if respoint[0]==team_num or respoint[0]==-1:
				team_respoints.append(respoint)
		if len(team_respoints)==0:
			raise RuntimeError("Team with number "+str(team_num)+" has no respoints.",0)
		if team_num not in self.__last_respoint:
			self.__last_respoint[team_num]=0
		if "first" in self.__restype:
			self.__last_respoint[team_num]=0
			return team_respoints[0]
		if "whileround" in self.__restype and mode=="roundstart":
			self.__last_respoint[team_num]=0
			return team_respoints[0]
		if "roundstart" in self.__restype and mode=="normal":
			return self.__respoints[self.__last_respoint[team_num] ]
		if "random" in self.__restype:
			respoint=random.Random().choice(team_respoints)
			self.__last_respoint[team_num]=team_respoints.index(respoint)
			return repoint
		if "toggle" in self.__restype:
			self.__last_respoint[team_num]=self.__last_respoint[team_num]+1
			if self.__last_respoint[team_num]>=len(team_respoints):
				self.__last_respoint[team_num]=0
			return team_respoints[self.__last_respoint[team_num]]
		raise RuntimeError("Type not known.",1)

	## @brief Adds a zone
	 # @details Adds the given zone to the internal zone list.
	 # @param team The number of the team for which the zone should be spawned, or None
	 #             if it should be spawned for all teams.
	 # @param zone The zone to add
	def addZone(self, team, zone):
		self.__zones.append( (team,zone) )

	## @brief Remove all zones
	 # @details Remove all zone from the internal zone list.
	def removeZones(self):
		self.__zones=list()

	## @brief Get zones
	 # @details Get the internal zone list.
	 # @return The internal zone list.
	def getZones(self):
		return self.__zones

	## @brief Returns an escaped name for the mode
	 # @details Returns the mode name with all spaces replaced by underscores and all letters lowercased.
	 # @return The escaped mode name.
	def getEscapedName(self):
		return self.name.replace(" ","_").lower()

	## @brief Returns current object state.
	 # @details Used by pickle and other serializing modules.
	 # @return A dictionary of the current object state
	def __getstate__(self):
		__state=dict()
		for var in self.__slots__:
			if var not in self.__not_persistent:
				varname=var
				settingsname=var
				if var.startswith("__"):
					varname=var.replace("__","_Mode__",1)
					settingsname=var.replace("__","",1)
					if hasattr(self, settingsname):
						continue # Ignore private variables if a public one with the same name exists.
				__state[settingsname]=getattr(self, varname)
		return __state

	## @brief Sets the current object state
	 # @details Used by pickle and other serializing modules.
	 # @param state The state to which to set the current object state.
	def __setstate__(self, state):
		self.__init__(state['name'])
		for var, value in state.items():
			if var not in self.__not_persistent:
				if not var in self.__slots__:
					var="__"+var
					if not var in self.__slots__:
						raise Exception("Error: Invalid state (var "+str(var)+" doesn't exist.)")
					else:
						var="_Mode"+var
				setattr(self, var, value)

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
