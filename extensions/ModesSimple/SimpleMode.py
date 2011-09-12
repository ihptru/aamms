import yaml
import os.path
import Armagetronad
import Global
from glob import glob
import LadderLogHandlers
import Player

modes=dict()

def SaveModes(dir="ModesSimple", ext=".mod", modename=None):
    global modes
    if not dir.endswith("/"):
        dir=dir+"/"
    if not os.path.exists(dir):
        os.mkdir(dir)
    if modename==None:
        for mode in modes.values():
            f=open(dir+mode.getEscapedName()+ext,"w")
            yaml.dump(mode, f)
    else:
        if modename in modes:
            f=open(dir+modename+ext,"w")
            yaml.dump(modes[modename], f)
            
def LoadModes(dir="ModesSimple", ext=".mod"):
    if not os.path.exists(dir):
        return
    global modes
    if not dir.endswith("/"):
        dir=dir+"/"
    modefiles=glob(dir+"*"+ext)
    for filename in modefiles:
        f=open(filename, "r")
        m=yaml.load(f)
        modes[m.getEscapedName()]=m

class Mode(yaml.YAMLObject):
    yaml_tag="!simplemode"
    
    def __init__(self, name, desc=None, map=None, lives=1):
        global modes
        
        if not desc:
            desc=name
        self.name=name
        self.desc=desc
        self.map=map
        self.lives=lives
        
        modes[self.getEscapedName()]=self
        
    def activate(self, kill=None):
        if kill==None:
            if LadderLogHandlers.roundStarted is True:
                kill=True
            else:
                kill=False
        mapfile=os.path.exists(os.path.join(Global.datadir, "included", self.map) )
        if not os.path.exists(mapfile):
            mapfile=os.path.exists(os.path.join(Global.datadir, "automatic", self.map) )
        if not os.path.exists(mapfile):
            return False
        Armagetronad.SendCommand("MAP_FILE "+mapfile)
        if kill:
            for player in Player.players:
                player.kill()
        return True
    def playerCrashed(self, laddername):
        p=Player.players[laddername]
        if "respoint" in p.data:
            p.respawn(*p.data["respoint"], force=False)
        else:
            Armagetronad.PrintMessage("Player "+p.getLadderName()+" doesn't exists in script.")
    def getEscapedName(self):
        return self.name.replace(" ","_").lower()