## @file Zone.py
#  @package Zone
#  @brief Functions and classes for zone management
#  @details This file contains functions and classes that are used for zone management.

import Armagetronad
import logging #@UnusedImport
import logging.handlers
import Team
import yaml
import time
from multiprocessing import Process as Thread
## @brief The logging object
# @private
# @details Used for logging by this module
# @note To enable or disable logging of this module use \link Team.enableLogging\endlink
log=logging.getLogger("TeamModule")
log.addHandler(logging.NullHandler() )

## @brief All available zone types
# @details List of all available zone types used to determine if a zone type is valid.
_ZONE_TYPES=["win", "death", "ball", "ballTeam", "blast", "deathTeam", "koh", 
             "fortress", "flag","rubber", "sumo", "target", "teleport", "zombie",
             "zombieOwner"]

## @brief All zone types that are defended.
# @details List of zone types you don't need when you attack.
_ZONE_TYPES_DEF=["fortress", "flag"]

## @class Zone.Zone
# @brief A zone
# @details This class represents a zone. Zones can be spawned, collapsed, have a name, ...
class Zone(yaml.YAMLObject):
    
    ## @property __name
    # @brief Used to store the name
    # @details Internal variable for the name.
    # @internal
     
    ## @property color
    # @brief The zone color
    # @details The color of the zone is the tuple of r,g,b. The maximal values 
     #          for each r, g or b are 1.
    
    ## @property position
    # @brief The position of the zone.
    # @details Tuple of x,y
    
    ## @property radius
    # @brief Zone radius
    # @details The radius of the zone.

    ## @property __alive
    # @brief Is the zone still alive?
    # @details True if yes, False if no.
    
    ## @property growth
    # @brief The growth of the zone
    # @details How much should the zone grow?
    
    ## @property __type
    # @brief The type of the zone
    # @details Could be: win, death, ball, ballTeam, blast, deathTeam, koh, fortress, flag,
     #                    rubber, sumo, target, teleport, zombie, zombieOwner
    
    ## @property interactive
    # @brief Should the zone bounce at walls?
    # @details True if yes, False if no.

    ## @property dir
    # @brief Direction in which the zone should move.
    # @details Tuple of xdir and ydir. 0,0 if the zone shouldn't move.

    ## @property target_size
    # @brief max or min size of the zone
    # @details Max or min radius of the zone, depends on the zone shrinks or expands.

    ## @property teamnames
    # @brief The team name(s) of the team(s) to pass to the zone before x and y.
    # @details The escaped name of the teams or None when no teams should be passed.
    
    ## @property settings
    # @brief Zone type specific settings
    # @details List of settings.
    
    ## @property killteam
    # @brief Kill the team when the zone collapses?
    # @details True if yes, False otherwise.

    ## @property teleport_settings
    # @brief Extra settings for teleport zones
    # @details This setting is needed because the different types of zones has different
     #          settings. The extra settings are allways at the end, except for teleport 
     #          zones. This settings are passed to SPAWN_ZONE at this position, but only
     #          if the zone is a teleport zone.

    ## @brief slots
    # @internal
    # @details See docs.python.org OOP Slots
    __slots__=("name","__name","color", "position", "radius","__alive", "growth","interactive", 
              "teamnames", "settings", "killteam", "target_size", "teleport_settings","dir","__type")

    ## @brief Yaml settings
    # @details See http://pyyaml.org/wiki/PyYAMLDocumentation for details to the PyYaml library.
    # @internal
    # @cond
    yaml_tag="!zone"
    ## @endcond

    ## @brief Which variables shouldn't be saved by object serializion?
    # @details Variables to exclude in __get_state__
    # @internal
    __not_persistent=("__alive", "teamnames")
    
    ## @brief Init function (Constructor)
    # @details Inits a new Zone and adds properties.
    # @param name The name of the zone
    # @param position Tuple of the x and y coordinate of the position of the zone.
    # @param radius Zone size (radius)
    # @param growth \copybrief growth
    # @param direction \copybrief dir
    # @param interactive \copybrief interactive
    # @param color Tuple of the r,g,b values of the color used for the zone,
    # @param target_size \copybrief target_size
    # @param type The zone type
    def __init__(self, name, position=(0,0), radius=5, growth=0,direction=(0,0), 
                 interactive=False, color=(0,0,1), target_size=-1,type="target" ):
        self.__name=name 
        self.position=position
        self.radius=radius
        self.growth=growth
        self.__alive=False
        self.color=color
        self.interactive=interactive
        self.dir=direction
        self.target_size=target_size
        self.teamnames=[]
        self.killteam=False
        self.settings=[]
        self.teleport_settings=[]
        self.setType(type)

    ## @brief Spawns the zone
    # @details Spawns the zone and sets alive to True
    # @param delay Spawn after delay secounds.
    def spawn(self, delay=0):
        if delay != 0:
            def run(delay, func):
                time.sleep(delay)
                func()
            t=Thread(None, run, args=(delay, self.spawn))
            t.daemon(True)
            t.start()
            return
        name=""
        command=""
        teams=list()
        command=str("SPAWN_ZONE {name} {type} {teams} {x} {y} {radius} {grow} {dirx} {diry} "
                "{tele_settings} {ztss} {intera} {r} {g} {b} {ts}")
        if self.name != None and self.name.strip()!="":
            name="n "+self.name.replace(" ","_")
        if len(self.teamnames)!=0:
            for team in self.teamnames:
                if team not in Team.teams:
                    if self.name != None:
                        log.error("Team assigned with zone „"+self.name+"“ doesn't exist.")
                    else:
                        log.error("Team assigned with zone doesn't exist")
                else:
                    if team == "ai":
                        team="ai_team"
                    teams=teams+[team]
        teams=" ".join(teams)
        tele_settings=""
        if self.__type=="teleport":
            tele_settings=" ".join(self.teleport_settings)
        settings=(" ").join(self.settings)
        x,y=self.position
        r,g,b=self.color
        dirx,diry=self.dir
        settings=" ".join(self.settings)
        Armagetronad.SendCommand(
                       command.format(name=name, type=self.__type, teams=teams, x=x, y=y, 
                    radius=self.radius, grow=self.growth, dirx=dirx, diry=diry, 
                    intera=self.interactive, r=r,g=g,b=b, ts=self.target_size, 
                    tele_settings=tele_settings,ztss=settings) 
                   )
        self.__alive=True
        if name == "":
            name="Unnamed"
        log.info("Zone „"+name.replace("n ","")+"“ spawned.")
    ## @brief Collapses the zone
    # @details Collapses the zone and sets alive to false
    # @warning If the zone name is None, all zones with no name are collapsed.
    def collapse(self):
        name=""
        if self.name != None:
            name=self.name.replace(" ","_")
        SendCommand("COLLAPSE_ZONE {0}".format(name) )
        if self.killteam and len(self.teamnames)!=0 and len(self.teamnames)==1:
            if self.teamnames[0] not in Team.teams:
                if self.name != None:
                    log.error("Team assigned with zone „"+self.name+"“ doesn't exist.")
                else:
                    log.error("Team assigned with zone doesn't exist")
            else:
                Team.teams[self.teamnames[0]].kill()
        self.__alive=False
        if name == "":
            name="Unnamed"
        log.info("Zone „"+name+"“ collapsed.")
    
    ## @brief Gets the zone name
    # @return The zone name or None if the zone is unnamed.
    @property
    def name(self):
        return self.__name

    ## @brief Sets the zone name
    # @param newname The new name of the zone or None if the zone should be unnamed.
    # @note This triggers the event "Zone renamed"
    @name.setter
    def setName(self, newname):
        self.__name=newname

    ## @brief Returns the alive state of the zone
    # @return True if the zone is alive, False otherwise.
    def isAlive(self):
        return self.__alive

    ## @brief Sets the zone type
    # @details For more information about zone types go to 
     #          http://crazy-tronners.com/wiki/index.php/Settings#type
    # @param ztype The name of the zone type.
    # @exception ValueError Raised if the zone type doesn't exist.
    def setType(self, ztype):
        if ztype not in _ZONE_TYPES:
            raise ValueError("Wrong zone type.",0)
        self.__type=ztype

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
                    varname=var.replace("__","_Zone__",1)
                    settingsname=var.replace("__","",1)
                if (hasattr(self, settingsname) and settingsname!=varname) or not hasattr(self, varname):
                    continue # Ignore private variables if a public one with the same name exists.
                __state[settingsname]=getattr(self, varname)
        return __state

    ## @brief Sets the current object state
    # @details Used by pickle and other serializing modules.
    # @param state The state to which to set the current object state.
    def __setstate__(self, state):
        for var, value in state.items():
            if not var in self.__slots__:
                var="__"+var
                if not var in self.__slots__:
                    raise Exception("Error: Invalid state (var "+str(var)+" doesn't exist.)")
                else:
                    var="_Zone"+var
            try:
                setattr(self, var, value)
            except AttributeError:
                if "__"+var in self.__slots__:
                    setattr(self, "_Zone__"+var,value)
        self.__alive=False
        self.teamnames=list()

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
