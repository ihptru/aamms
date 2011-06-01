#!/usr/bin/env python3
## @file Global.py
 # @brief Global functions and variables
 # @details This file contains global functions and variables.

import Player
import Armagetronad
import yaml
import Mode

## @brief Call to reload player list.
 # @details This will kill all players and reset match score so the script can reload the player list.
def reloadPlayerList():
	Armagetronad.SendCommand("START_NEW_MATCH")
	Armagetronad.SendCommand("CYCLE_RUBBER -1")
	Armagertronad.SendCommand("CYCLE_RUBBER 1")
