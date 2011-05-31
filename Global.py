#!/usr/bin/env python3
## @file Global.py
 # @brief Global functions and variables
 # @details This file contains global functions and variables.

import Player
import Armagetronad

## @brief Call to reload player list.
 # @details This will kick all players to the server (so they leave and come back) to reload player list.
def reloadPlayerList():
	Armagetronad.SendCommand("DEFAULT_KICK_TO_SERVER "+"127.0.0.1")
	Armagetronad.SendCommand("DEFAULT_KICK_TO_REASON Sorry, the server's script crashed. All players have to rejoin to reload the script's player list. ")
	for ln, player in Player.players.items():
		Armagetronad.SendCommand("KICK_TO "+ln)
		Armagetronad.SendCommand("UNBAN_USER "+ln)
		Armagetronad.SendCommand("UNBAN_IP "+Player.players[ln].ip)
		del Player.players[ln]
