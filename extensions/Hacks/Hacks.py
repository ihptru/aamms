## @file Hacks.py
#  @brief This file contains commands that allows players to cheat, like /tele.

import Player
import Armagetronad
import Commands
import Messages

## @brief Teleports a player to the given position.
#  @details Teleports the given player to the given position.
#  @param x The x coordinate to which to teleport
#  @param y The y coordinate to which to teleport
#  @param xdir The x direction
#  @param ydir The y direction
#  @param player_name The player which you like to teleport. If set to None, you teleport yourself.
def tele(acl, player, x, y, xdir=0, ydir=1, player_name=None):
    if player_name!=None:
        if player_name not in Player.players:
            Armagetronad.PrintPlayerMessage("0xff0000Invalid player!")
            return
        Armagetronad.SendCommand("RESPAWN_PLAYER "+player_name+" 0 "+" ".join((x,y,xdir,ydir)))
        Armagetronad.SendCommand("TELEPORT_PLAYER "+player_name+" "+" ".join((x,y,xdir,ydir)))
        Armagetronad.PrintMessage(Messages.PlayerTeleported.format(player=Player.players[player_name].name, by=player, x=x,y=x) )
    else:
        Armagetronad.SendCommand("RESPAWN_PLAYER "+player+" 0 "+" ".join((x,y,xdir,ydir)))
        Armagetronad.SendCommand("TELEPORT_PLAYER "+player+" "+" ".join((x,y,xdir,ydir)))
        Armagetronad.PrintMessage(Messages.PlayerSelfTeleport.format(player=player,x=x,y=y) )

## @brief Changes your lives.
#  @param lives new lives
def lives(acl, player, lives):
    try:
        lives=int(lives)+1
    except ValueError:
        Armagetronad.PrintPlayerMessage(player, "0xff0000Wrong value for argument lives!")
        return
    Player.players[player].setLives(lives)
    Armagetronad.PrintPlayerMessage(player, "0xff0000Your lives left: "+str(lives-1) )

Commands.add_help_group("Hacks", "Some commands that allow cheating")
Commands.register_commands(lives, tele, group="Hacks")
