# advancedpoi.py
# Author: Quentin Goss
# A library for doing usefull things with POIs.
import os

class POIType():
    def __init__(self,name):
        self.name = name# Type ID
        #self.pois = []  # List of inclusive POIs
        return

# Translates an xy string to (x,y) coordinates
#
# Right click -> Copy Cursor Position
# Something like 568.47,399.78 is the Result
#
# @param string s_xy = coordinates in string format
# @return (x,y) =  x,y coordinates as a tuple of floats
def xystring2float(s_xy):
    ls_xy = s_xy.split(',')
    return (float(ls_xy[0]),float(ls_xy[1]))
    
def colorstring2float(s_color):
    s_color = s_color[s_color.index('(')+1:s_color.index(')')]
    rgb = s_color.split(',')
    return (rgb[0],rgb[1],rgb[2])

# Parses a POI hotfile
# @param hotfile = path to hotfile where pois are at
def parse_hotfile(hotfile='poi.hot'):
    class POI():
        def __init__(self,_type,x,y,color):
            self._type = _type
            self.x = x
            self.y = y
            self.color = color
            return
    pois = [] # Holds POIs
    
    _type = ''# Last seen type
    color = (255,255,255)
    with open(hotfile,'r') as hf:
        for line in hf:
            # Clean up the line
            line.strip()
            if '\n' in line: line = line[:-1]
            
            # Comment, ignore line
            if len(line) == 0 or line[0] == '#' or line[0] == ' ':
                continue

            # Type enclosed in ""
            if line.count('"') == 2:
                _type = line.strip('"')
                continue
            
            if line.count(',') == 2:
                color = colorstring2float(line)
                continue
                
            # Line must be a coordinate
            if line.count(',') == 1:
                x,y = xystring2float(line)
                pois.append(POI(_type,x,y,color))
                continue
            continue
    return pois

# Parses through the poi hotfile and adds pois with traci
# @param traci = traci instance
global HIST_SZ
def poi_parse_and_place(traci):
    hotfile = 'poi.hot'
    pois = parse_hotfile(hotfile)
    n_pois = 0
    for poi in pois:
        traci.poi.add('poi%s' % (n_pois),poi.x,poi.y,poi.color,poiType=poi._type)
        n_pois += 1
        continue
    global HIST_SZ
    HIST_SZ = os.stat(hotfile).st_size
    return

# Remove all pois from traci
# @param traci = traci instance
def remove_all_pois(traci):
    poi_ids = traci.poi.getIDList()
    for poi in poi_ids:
        traci.poi.remove(poi)
    return

# Things that are to be done on the initialize step.
# @param traci = traci instance
def initialize(traci):
    poi_parse_and_place(traci)
    return

# Things that happen every timestep
# @param traci = traci instance
def timestep(traci):
    hotfile = 'poi.hot'
    new_sz = os.stat(hotfile).st_size
    global HIST_SZ
    if HIST_SZ != new_sz:
        remove_all_pois(traci)
        poi_parse_and_place(traci)
    return


def test():
    import time; import os
    hotfile = 'poi.hot'
    hist_sz = os.stat(hotfile).st_size
    while True:
        print('%d                                  ' % (hist_sz), end='\r')
        if hist_sz != os.stat(hotfile).st_size:
            hist_sz = os.stat(hotfile).st_size
            try:
                parse_hotfile()
            except:
                print("Error while parsing. Check file.",end='\r')
        time.sleep(1)
    return
    
if __name__ == "__main__":
    test()
