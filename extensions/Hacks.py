## @file Hacks.py
 # @brief This file contains commands that allows players to cheat, like /tele.

import Player
import Armagetronad
import Commands
import Messages

## @brief Teleports a player to the given position.
 # @details Teleports the given player to the given position.
 # @param x The x coordinate to which to teleport
 # @param y The y coordinate to which to teleport
 # @param xdir The x direction
 # @param ydir The y direction
def tele(acl, player, x, y, xdir=0, ydir=1):
	Player.players[player].respawn(x,y,xdir,ydir,True)
	Armagetronad.PrintMessage(Messages.PlayerTeleport.format(player=player,x=x,y=y,xdir=xdir, ydir=ydir) )

## @brief Changes your lives.
 # @param lives new lives
def lives(acl, player, lives):
	try:
		lives=int(lives)
	except ValueError:
		Armagetronad.PrintPlayerMessage(player, "0xff0000Wrong value for argument lives!")
		return
	Player.players[player].setLives(lives)
	Armagetronad.PrintPlayerMessage(player, "0xff0000Lives changed to "+str(lives) )

Commands.register_commands(lives, tele)
