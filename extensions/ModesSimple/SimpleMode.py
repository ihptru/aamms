import yaml
import os.path
import Armagetronad
import Global

modes=[]

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

class Mode(yaml.YAMLObject):
    yaml_tag="!mode"
    
    def __init__(self, name, desc=None, map=None, lives=1):
        global modes
        
        if not desc:
            desc=name
        self.name=name
        self.desc=desc
        self.map=map
        self.lives=lives
        
        modes.append(self)
        
    def activate(self):
        mapfile=os.path.exists(os.path.join(Global.datadir, "included", self.map) )
        if not os.path.exists(mapfile):
            mapfile=os.path.exists(os.path.join(Global.datadir, "automatic", self.map) )
        if not os.path.exists(mapfile):
            return False
        Armagetronad.SendCommand("MAP_FILE "+mapfile)
        
        return True
    def playerCrashed(self, laddername):
        