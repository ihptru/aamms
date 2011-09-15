#!/usr/bin/env python3
import LadderLogHandlers
import logging
import Team
import Armagetronad
import Zone
import Global
import Commands
import AccessLevel
import Poll
import Player

if "log" not in globals():
    log=logging.getLogger("MainModule")
    h=logging.StreamHandler()
    h.setLevel(logging.DEBUG)
    f=logging.Formatter("[%(name)s] (%(asctime)s) %(levelname)s: %(message)s")
    h.setFormatter(f)
    log.addHandler(h)
    log.setLevel(logging.INFO)

def exit(normal=False, quiet=False):
    if normal:
        AccessLevel.save()
    if not quiet:
        log.info("Exit")
    if normal:
        Armagetronad.PrintMessage("0xff0000Script exited.")
    else:
        Armagetronad.PrintMessage("0xff0000Script crashed.")

def main(debug=False, disabledCommands=[]):
    #We need some special settings. Set it
    Armagetronad.SendCommand("LADDERLOG_WRITE_ONLINE_PLAYER 1")
    Armagetronad.SendCommand("LADDERLOG_WRITE_CYCLE_CREATED 1")
    Armagetronad.SendCommand("LADDERLOG_WRITE_INVALID_COMMAND 1")
    Armagetronad.SendCommand("INTERCEPT_UNKNOWN_COMMANDS 1")
    Armagetronad.SendCommand("LADDERLOG_GAME_TIME_INTERVAL 1")
    Armagetronad.SendCommand("EXTRA_ROUND_TIME 1")
    if Global.debug:
        log.info("Starting in debug mode.")
        Player.enableLogging(logging.DEBUG)
        Team.enableLogging(logging.DEBUG)
        LadderLogHandlers.enableLogging(logging.DEBUG)
        Poll.enableLogging(logging.DEBUG)
        Zone.enableLogging(logging.DEBUG)
    else:
        Player.enableLogging(logging.WARNING)
        Team.enableLogging(logging.WARNING)
        LadderLogHandlers.enableLogging(logging.INFO)
        Poll.enableLogging(logging.WARNING)
        Zone.enableLogging(logging.WARNING)

    Commands.disabled=Commands.disabled+disabledCommands    
    #Init
    AccessLevel.load()
    log.info("Script started")    
    Armagetronad.PrintMessage("0xff0000Script started")
    #We need to refresh player list
    Global.reloadPlayerList()
    while(True):
        line=""
        try:
            line=input()
        except KeyboardInterrupt:
            log.info("Exiting")
            break
        line=line.strip()
        keywords=line.split(" ")
        command=keywords[0]
        args=keywords[1:]
        del keywords
        #make command name CamelCase
        real_commandname=command.upper()
        command=command.lower()
        command=command.replace("_"," ")
        command=command.title()
        command=command.replace(" ","")
        #call handler
        if(hasattr(LadderLogHandlers,command) ):
            try:
                getattr(LadderLogHandlers,command)(*args)
            except TypeError as e:
                if not debug:
                    log.error("Wrong arguments for ladder log handler for "+command+". This might be a bug.")
                else:
                    raise e
            except Exception as e:
                if Global.debug: raise(e)
                else:
                    log.error("Exception " +e.__class__.__name__ + " raised in Ladder log handler. This might be a bug.")
        if real_commandname in LadderLogHandlers.extraHandlers:
            for extraHandler in LadderLogHandlers.extraHandlers[real_commandname]:
                try: extraHandler(*args)
                except TypeError as e: 
                    log.error("Wrong arguments for extra ladderlog handler "+extraHandler.__name__)
                    if debug: raise e
                except Exception as e: 
                    log.error("Extra Ladderlog handler "+extraHandler.__name__+" raised an exception.")
                    if debug: raise e
if __name__=="__main__":
    main()
    exit(True)
