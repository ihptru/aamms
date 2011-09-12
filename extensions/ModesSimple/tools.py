from xml.etree import ElementTree
import math

## @brief Parse a XML file into an ElemenTree object
#  @param filename The name of the file which to parse.
#  @return An ElementTree object.
def ParseXML(filename):
    tree=ElementTree.parse(filename)
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
                value=math.sqrt(tanv**2 + 1) # 1² is 1
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
    # TODO
    pass 