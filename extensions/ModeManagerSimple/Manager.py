#import Commands
from xml.etree import ElementTree as etree
import math

maps_root=None

def ParseXML(filename):
    parser=etree.XMLParser()
    tree=etree.parse(filename, parser=parser)
    return tree
    
## @brief Parses a map file and returns respoints.
#  @details Takes a map file for Armagetron Advanced and extracts the respawn points.
#           This is needed for lives because if we don't parse map files, you'd need to
#           list each respoint for each map.
# @param map The ElementTree object of the map file.
# @return List of respoints (x,y,xdir, ydir)
def ParseRespoints(xml):
    respoints=[]
    for point in xml.getroot().findall("Map/World/Field/Spawn"):
        for i in point.attrib:
            if i.lower()=="angle":
                tanv=math.atan(float(point.attrib[i]))
                value=(tanv+1)**2
                ydir=-tanv/value
                xdir=1/value
            else:
                locals()[i.lower()]=float(point.attrib[i.lower()])
        respoints.append( (x, y, xdir, ydir) ) #@UndefinedVariable
    return respoints

## @brief Parses Zones of a Map into Zone objects.
#  @details Takes an armagetron advanced map and returns a list of Zone objects for each
#           Zone defined in the map.
#  @param xml The ElementTree object of the xml file.
#  @return List of Zone objects.
def ParseZones(xml):
    pass

## @brief Add a mode. 
#  @details Add a new mode.
#  @param name The name of the mode.
#  @param file The file which to include when the mode gets activated.
#  @param lives The lives each player should get in this mode.
#  @param desc The description of the mode.
def AddMode(acl, player, name, file, desc):
    pass

#Commands.add_help_group("ModeManager", "Commands for managing modes (Add, Edit, Remove)")
#Commands.register_commands(AddMode, group="ModeManager")