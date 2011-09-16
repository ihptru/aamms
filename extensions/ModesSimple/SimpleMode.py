import yaml
import os.path
import Armagetronad, Messages
from glob import glob
import LadderLogHandlers
import Player
import Global

modes=dict()
current_mode=None
mode_message_printed=False 

def SaveModes(dir="ModesSimple", ext=".mod", modename=None):
    global modes
    if not dir.endswith("/"):
        dir=dir+"/"
    if not os.path.exists(dir):
        os.mkdir(dir)
    if modename==None:
        for mode in modes.values():
            f=open(dir+mode.getEscapedName()+ext,"w")
            yaml.dump(mode, f, default_flow_style=False)
    else:
        if modename in modes:
            f=open(dir+modename+ext,"w")
            yaml.dump(modes[modename], f, default_flow_style=False)
            
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
    
    def __init__(self, name, desc=None, file=None, lives=1):
        global modes
        if not desc:
            desc=name
        self.name=name
        self.desc=desc
        self.file=file
        self.lives=int(lives)  
        modes[self.getEscapedName()]=self
        
    def activate(self, kill=None, first_time=None):
        global current_mode
        if not first_time:
            first_time = False if current_mode==self else True 
        if kill==None:
            if LadderLogHandlers.roundStarted is True:
                kill=True
            else:
                kill=False
        configfile=self.file
        if first_time:
            Armagetronad.SendCommand("SINCLUDE settings.cfg")
            Armagetronad.SendCommand("SINCLUDE default.cfg")
            Armagetronad.SendCommand("SINCLUDE "+configfile)
            Armagetronad.SendCommand("SINCLUDE settings_custom.cfg")
            server_name=Global.server_name
            Armagetronad.SendCommand("SERVER_NAME "+server_name+" 0xff8800["+self.name+"]")
        if kill:
            for player in Player.players.values():
                player.kill()
        current_mode=self
        global mode_message_printed
        if not mode_message_printed:
            Armagetronad.PrintMessage(Messages.ModeMessage.format(mode=self.name))
            mode_message_printed=True
        return True
    
    def playerCrashed(self, laddername):
        p=Player.players[laddername]
        if p.getLives() <= 1:
            return None
        elif "respoint" in p.data:
            p.crashed()
            p.respawn(*p.data["respoint"], force=False)
            return p.getLives()-1
        else:
            Armagetronad.PrintMessage("Player "+p.getLadderName()+" doesn't exists in script.")
        return False
            
    def getEscapedName(self):
        return self.name.replace(" ","_").lower() 