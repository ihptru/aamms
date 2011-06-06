#!/usr/bin/env python3
import LadderLogHandlers
import logging
import readline
import Player
import Team
import Event
import Armagetronad
import Zone
import Mode
import Global
import atexit
import sys
import os
import os.path

def exit():
	Mode.saveModes()
	Armagetronad.PrintMessage("0xff0000Script exited.")

os.chdir(os.path.dirname(sys.argv[0]) )
log=logging.getLogger("MainModule")
h=logging.StreamHandler()
h.setLevel(logging.DEBUG)
f=logging.Formatter("[%(name)s] (%(asctime)s) %(levelname)s: %(message)s")
h.setFormatter(f)
log.addHandler(h)
log.setLevel(logging.INFO)
Player.enableLogging()
Team.enableLogging()
LadderLogHandlers.enableLogging()
Mode.enableLogging()
#We need some special settings. Set it
Armagetronad.SendCommand("LADDERLOG_WRITE_ONLINE_PLAYER 1")
Armagetronad.SendCommand("LADDERLOG_WRITE_CYCLE_CREATED 1")
Armagetronad.SendCommand("LADDERLOG_WRITE_INVALID_COMMAND 1")
Armagetronad.SendCommand("INTERCEPT_UNKNOWN_COMMANDS 1")
Armagetronad.SendCommand("LADDERLOG_GAME_TIME_INTERVAL 1")
Armagetronad.SendCommand("EXTRA_ROUND_TIME 1")
Armagetronad.PrintMessage("0xff0000Script started")
#Init
Team.Add("AI")
Mode.loadModes()
Global.updateHelpTopics()
log.info("Script started")
#We need to refresh player list
Global.reloadPlayerList()
atexit.register(exit)
while(True):
	line=""
	try:
		line=input()
	except KeyboardInterrupt:
		log.info("Exiting")
		Armagetronad.PrintMessage("Script exited.")
		break
	line=line.strip()
	keywords=line.split(" ")
	command=keywords[0]
	args=keywords[1:]
	del keywords
	#beautify command name
	command=command.lower()
	command=command.replace("_"," ")
	command=command.title()
	command=command.replace(" ","")
	#call handler
	if(hasattr(LadderLogHandlers,command) ):
		try:
			getattr(LadderLogHandlers,command)(*args)
		except TypeError as e:
			log.warning("Wrong arguments for ladder log handler for "+command+". This might be a bug.")
			raise e
		except Exception as e:
			log.error("Exception " +e.__class__.__name__
			            + " raised in Ladder log handler. This might be a bug.")
			raise(e)
	else:
		log.debug("No ladder log handler for ladder event „" + command + "“.")
