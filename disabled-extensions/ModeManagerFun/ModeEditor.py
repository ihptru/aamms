import Armagetronad
import Global
import Poll
import LadderLogHandlers
import time
import Player
import Zone
import Mode

## @brief Enter the mode editor.
# @details This command changes the state to modeeditor.
# @param acl The accesslevel of the player
# @param playername The name of the player
def modeEditor(acl, player):
    if Global.state=="modeEditor":
        Armagetronad.PrintPlayerMessage(player, "0xff0000Already in mode editor state!")
    Armagetronad.SendCommand("INCLUDE settings.cfg")
    Armagetronad.SendCommand("SINCLUDE settings_custom.cfg")
    Armagetronad.SendCommand("DEFAULT_KICK_REASON Server\ under\ maintenance.")
    def setSettings():
        Armagetronad.SendCommand("ALLOW_TEAM_NAME_PLAYER 1")
        Armagetronad.SendCommand("FORTRESS_CONQUEST_TIMEOUT -1")
        Armagetronad.SendCommand("MAX_CLIENTS 1")
        Armagetronad.SendCommand("SP_TEAMS_MAX 1")
        Armagetronad.SendCommand("TEAMS_MAX 1")
        Armagetronad.SendCommand("SP_AUTO_AIS 0")
        Armagetronad.SendCommand("AUTO_AIS 0")
        Armagetronad.SendCommand("SP_NUM_AIS 0")
        Armagetronad.SendCommand("NUM_AIS 0")
        Armagetronad.SendCommand("CYCLE_SPEED_MIN 0")
        Armagetronad.SendCommand("CYCLE_RUBBER 10000000")
        Armagetronad.SendCommand("SP_WALLS_LENGTH 0.000001")
        Armagetronad.SendCommand("CYCLE_SPEED 5")
        Armagetronad.SendCommand("CYCLE_BRAKE -100")
        Armagetronad.SendCommand("CYCLE_BRAKE_DEPLETE 0")
        Armagetronad.SendCommand("CYCLE_SPEED_DECAY_ABOVE 1.5")
        Armagetronad.SendCommand("CYCLE_ACCEL 0")
        Armagetronad.SendCommand("SP_MIN_PLAYERS 0")
        Armagetronad.SendCommand("CYCLE_TURN_SPEED_FACTOR 1")
        Armagetronad.SendCommand("CYCLE_SPEED_DECAY_BELOW 2")
        Armagetronad.SendCommand("FORTRESS_SURVIVE_WIN 0")
    setSettings()
    Poll.Cancel()
    Mode.current_mode=None
    Armagetronad.SendCommand("NETWORK_AUTOBAN_FACTOR 0")
    Armagetronad.PrintPlayerMessage(player, "0xff0000Kicking other players ...")
    Armagetronad.PrintPlayerMessage(player, "\n"*4)
    for playero in Player.players.values():
        if playero.ip!=Player.players[player].ip:
            Armagetronad.SendCommand("KICK "+playero.getLadderName() )
        else:
            playero.kill()    
    Armagetronad.SendCommand("NETWORK_AUTOBAN_FACTOR 10")
    Armagetronad.SendCommand("LADDERLOG_WRITE_ADMIN_COMMAND 1")
    def HandleAdminCommand(player, ip, acl, *command):
        global data
        if Global.state!="modeeditor":
            LadderLogHandlers.unregister_handler("ADMIN_COMMAND", HandleAdminCommand)
        if(Armagetronad.IsSetting(command[0]) and len(command)>1):
            data["mode"].settings[command[0]]=" ".join(command[1:])
            Armagetronad.PrintMessage("0xff0000"+command[0]+" changed to "+" ".join(command[1:]))
            setSettings()
    LadderLogHandlers.register_handler("ADMIN_COMMAND", HandleAdminCommand)
    Global.state="modeeditor"
    global data
    data=dict()
    data["speed"]=5
    data["mode"]=Mode.Mode("Unsaved")
    data["stopped"]=False
    def PrintMessage():
        message="""0x00ffffWelcome to ModeEditor! 0xffffff
ModeEditor was made to help you creating new modes.
Use the /stop, /go, /lessSpeed, /moreSpeed and brake commands to controll the speed of the cycle.
To add a zone or a respawn point at the current position of your cycle use /makeZone and /makeRes.
If you want to go to a specific position, use /stop and then use /tele.
You can use /modeSetting to change settings like name and lives.
To change game settings like rubber you can use /admin (i.e. /admin CYCLE_RUBBER 5). Your changes will get recorded.
To save the mode use /saveMode to save the mode. 
If you want to go back to normal mode, use /normal."""
        for msg in message.split("\n"):
            Armagetronad.PrintMessage(msg)
            time.sleep(3)
    LadderLogHandlers.atRoundend.append(PrintMessage)
                

## @brief Go back to normal state.
# @details Changes the state to normal.
def normal(acl, player):
    Armagetronad.SendCommand("INCLUDE settings.cfg")
    Armagetronad.SendCommand("SINCLUDE settings_custom.cfg")
    Global.reloadPlayerList()
    if Mode.current_mode:
        Mode.current_mode.activate(True) #@UndefinedVariable (for Eclipse)
    for player in Player.players.values():
        player.kill()
    Global.state="normal"
    global data
    data=None

## @brief Stop the cycle.
# @details Stop the moving cycle.
def stop(acl, player):
    Armagetronad.SendCommand("CYCLE_SPEED_DECAY_ABOVE 10000000000000000000000000")
    Armagetronad.SendCommand("CYCLE_SPEED_DECAY_BELOW 10000000000000000000000000")
    Armagetronad.SendCommand("CYCLE_SPEED 0")
    global data
    data["stoppped"]=True

## @brief Let the cycle move again.
# @details Sets CYCLE_SPEED to data["speed"]
def go(acl, player):
    global data
    Armagetronad.SendCommand("CYCLE_SPEED_DECAY_ABOVE 1.5")
    Armagetronad.SendCommand("CYCLE_SPEED_DECAY_BELOW 2")
    Armagetronad.SendCommand("CYCLE_SPEED "+str(data["speed"]) )
    data["stopped"]=False

## @brief Incrase or set the speed of the cycle.
# @param speed If given, the speed is set to this value. Otherwise it will be incrased by 5.
def moreSpeed(acl, player, speed=None):
    global data
    if speed!=None:
        try:
            data["speed"]=float(speed)
        except:
            data["speed"]=float(data["speed"])+5
    else:
        data["speed"]=float(data["speed"])+5
    if not data["stopped"]:
        Armagetronad.SendCommand("CYCLE_SPEED "+str(data["speed"]) )

## @brief Decrase the speed of the cycle.
def lessSpeed(acl, player):
    global data
    data["speed"]=float(data["speed"])-5
    if data["speed"]<0:
        data["speed"]=0
    if not data["stopped"]:
        Armagetronad.SendCommand("CYCLE_SPEED "+str(data["speed"]) )

## @brief Create a zone at the current position of the cycle.
# @param name The name of the zone.
# @param type The type of the zone (Win, death, deathTeam, fortress, ....)
# @param size The radius of the zone.
# @param grow The zone growth. Negative values will let the zone shrink.
# @param r Red
# @param g Green
# @param b Blue
# @param team The team for which the zone should get spawned. 
#             -1 if the zone doesn't belong to any team. 
#              0 if the zone should be spawned once for every team.
# @param extrasettings Additional settings for the zone type (like <rubber> for rubber zones)
def makeZone(acl, player, name,type,size, grow="0", team="-1",r=0,g=0,b=15, extrasettings=""):
    if type not in Zone._ZONE_TYPES :
        Armagetronad.PrintMessage("0xff0000Invalid zone type!")
        return
    cur_pos=Armagetronad.GetPlayerPosition(player)[:2]
    global data
    z=Zone.Zone(name=name, radius=float(size), growth=float(grow), type=type, color=(int(r),int(g),int(b)), position=cur_pos)
    z.settings=extrasettings.split(" ")
    try:
        team=int(team)
    except ValueError:
        Armagetronad.PrintMessage("0xff0000Invalid value for argument team!")
        return
    if team==0:
        team=None
    data["mode"].addZone(team, z)
    if team!=-1 or type in ["fortress", "flag", "deathTeam", "ballTeam"]:
        z.teamnames=[Player.players[player].getTeam()]
    z.spawn()
    Armagetronad.PrintMessage("0xffff00Added "+type+" zone at "+"|".join(map(str, cur_pos)))

## @brief Create a respoint at the current position of the cycle.
# @param team The number of the team for which the respoint should be used. -1 if the respoint should be used for all teams.
def makeRes(acl, player, team=-1):
    try:
        team=int(team)
    except ValueError:
        Armagetronad.PrintMessage("0xff0000Invalid value for argument team!")
        return
    x,y,xdir,ydir=Armagetronad.GetPlayerPosition(player)
    global data
    data["mode"].addRespoint(x,y,xdir,ydir, team)
    Armagetronad.PrintMessage("0xffff00Added respoint at "+str(x)+"|"+str(y)+" for the team with the number "+str(team))

## @brief Set mode settings
# @param setting one of: name, short_name, settings_file, max_teams, max_team_members, lives.
# @param value The value to which the setting should be set. If not given, the current value of the settings is printed.
def modeSetting(acl, player, setting, *value):
    if len(value)!=0:
        value=" ".join(value)
    else:
        value=None
    global data
    if setting in ["max_teams","max_team_members","lives", "arena_size"] and value!=None:
        try:
            value=int(value)
        except ValueError:
            Armagetronad.PrintMessage("0xff0000Invalid value!")
            return
    if setting in ["name", "short_name", "settings_file", "max_teams", "max_team_members","lives"]:
        if value!=None:
            setattr(data["mode"], setting, value)
            Armagetronad.PrintMessage("{0} was set to {1}".format(setting, str(value) ) )
        else:
            Armagetronad.PrintMessage("{0} is currently set to {1}".format(setting, str(getattr(data["mode"], setting) ) ) )
    #elif setting in ["arena_size"]:
    #    if value:
    #        data["mode"].settings[setting]=value
    #        Armagetronad.SendCommand(setting+str(value));
    else:
        Armagetronad.PrintMessage("0xff0000Invalid setting!")
    return

## @brief Save the mode with its current settings.
def saveMode(acl, player):
    global data
    Mode.modes[data["mode"].getEscapedName()]=data["mode"]
    Mode.saveModes(modename=data["mode"].getEscapedName())
    Armagetronad.PrintMessage("0x00ff00Saved mode")    

## @brief Test the mode.
def testMode():
    global data
    m=Mode.current_mode
    data["mode"].activate()
    Mode.current_mode=m

## @brief Load a mode to edit.
# @param mode The mode to load. For a list of available modes see /info modes.
def loadMode(acl, player, mode):
    global data
    for k,m in Mode.modes.items():
        if k==mode or m.short_name==mode:
            mode=m
            break
    else:
        Armagetronad.PrintMessage(Messages.ModeNotExist.format(mode=mode) )
    data["mode"]=mode
    mode.activate(False)
    Mode.current_mode=None