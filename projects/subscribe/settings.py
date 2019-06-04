import os
class Settings(object):
	default = "C:/sumo-windows10/projects"
	map_path = os.path.join(default, "grid3/data/grid3.net.xml")
	radius = 100 #searching around 100miles out
	sumo_config = os.path.join(default, "grid3/data/grid3.sumocfg")
