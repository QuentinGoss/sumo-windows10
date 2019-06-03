import os
class Settings(object):
	default = "E:/Python/sumo-windows10/projects"
	map_path = os.path.join(default, "grid2/data/grid2.net.xml")
	radius = 100 #searching around 100miles out
	sumo_config = os.path.join(default, "grid2/data/grid2.sumocfg")