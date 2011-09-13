from . import SimpleMode
import Messages, Armagetronad, Player, LadderLogHandlers

RESPAWN_EVENTS=["DEATH_SUICIDE","DEATH_TEAMKILL", "DEATH_DEATHZONE", "DEATH_FRAG", "DEATH_SHOT_FRAG", "DEATH_SHOT_SUICIDE", "DEATH_SHOT_TEAMKILL"]

def HandlePlayerDied(player, *args):
    if SimpleMode.current_mode:
        lives_left=SimpleMode.current_mode.playerCrashed(player) #@UndefinedVariable
        message=Messages.PlayerDied.format(player=Player.players[player].name)
        if lives_left is not None: #@UndefinedVariable
            res_msg=Messages.LivesMsg.format(lives=lives_left)
            if lives_left==0:
                res_msg=Messages.LastLifeMsg
            elif lives_left==1:
                res_msg=Messages.OneLifeMsg
            message=Messages.PlayerRespawned.format(player=Player.players[player].name, msg=res_msg) 
        Armagetronad.PrintMessage(message)
    
def HandleCycleCreated(player_name, x, y, xdir, ydir):
    Player.players[player_name].data["respoint"]=tuple( map( float,(x,y,xdir,ydir) ) )

def HandleNewRound(*args):
    if SimpleMode.current_mode:
        for player_name in Player.players:
            Player.players[player_name].setLives(SimpleMode.current_mode.lives) #@UndefinedVariable
    
for respawn_event in RESPAWN_EVENTS:
    LadderLogHandlers.register_handler(respawn_event, HandlePlayerDied)
LadderLogHandlers.register_handler("CYCLE_CREATED", HandleCycleCreated)
LadderLogHandlers.register_handler("NEW_ROUND", HandleNewRound)

def onShutdown():
    for respawn_event in RESPAWN_EVENTS:
        LadderLogHandlers.unregister_handler(respawn_event, HandlePlayerDied)
    LadderLogHandlers.unregister_handler("CYCLE_CREATED", HandleCycleCreated)
    LadderLogHandlers.unregister_handler("NEW_ROUND", HandleNewRound)