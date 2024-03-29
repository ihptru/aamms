#!/usr/bin/env python3
import AccessLevel
import LadderLogHandlers
import logging
import Team
import Armagetronad
import Global
import Commands
import Poll
import Player
import time
import inspect

log=logging.getLogger("MainModule")

def exit(normal=True, quiet=False):
    AccessLevel.save()
    if not quiet:
        log.info("Exit")
        if normal:
            Armagetronad.PrintMessage("0xff0000Script exited.")
        else:
            Armagetronad.PrintMessage("0xff0000Script crashed.")

def main(debug=False, disabledCommands=[], reloaded=False):
    if not reloaded:
        h=logging.StreamHandler()
        h.setLevel(logging.DEBUG)
        f=logging.Formatter("[%(name)s] (%(asctime)s) %(levelname)s: %(message)s")
        h.setFormatter(f)
        log.addHandler(h)
        log.setLevel(logging.INFO)
    #We need some special settings. Set it
    Global.set_script_settings()
    for x in dir(LadderLogHandlers):
        if not x[0].isupper():
            continue
        if inspect.isfunction(getattr(LadderLogHandlers,x)):
            x="".join([i.upper() if i.islower() else "_"+i for i in x])
            Armagetronad.SendCommand("LADDERLOG_WRITE"+x+" 1") # X has already a underscore at beginning.
    if not reloaded:
        if Global.debug:
            log.info("Starting in debug mode.")
            Player.enableLogging(logging.DEBUG)
            Team.enableLogging(logging.DEBUG)
            LadderLogHandlers.enableLogging(logging.DEBUG)
            Poll.enableLogging(logging.DEBUG)
        else:
            Player.enableLogging(logging.WARNING)
            Team.enableLogging(logging.WARNING)
            LadderLogHandlers.enableLogging(logging.INFO)
            Poll.enableLogging(logging.WARNING)

    Commands.disabled=Commands.disabled+disabledCommands    
    #Init
    AccessLevel.load()
    if not reloaded:
        log.info("Script started")    
        Armagetronad.PrintMessage("0xff0000Script started")
    else:
        log.info("Script reloaded")
    #We need to refresh player list
    Global.reloadPlayerList()
    while(True):
        line=""
        if Global.handleLadderLog==False:
            time.sleep(1)
            continue
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
                getattr(LadderLogHandlers,command)(*args)
        if real_commandname in LadderLogHandlers.extraHandlers:
            for extraHandler in LadderLogHandlers.extraHandlers[real_commandname]:
                try: extraHandler(*args)
                except TypeError as e: 
                    log.error("Extension "+extraHandler.__package__+" registered a wrong ladderlog handler. This is a bug.")
                    if debug: raise e
if __name__=="__main__":
    main()
    exit(True)
