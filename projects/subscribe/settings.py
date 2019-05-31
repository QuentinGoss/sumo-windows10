import os
class Settings(object):
	default = "E:/Python/NSFSimulation"
	map_path = os.path.join(default, "maps/cologne/edges.json")
	radius = 100 #searching around 100miles out
	sumo_config = os.path.join(default, "simulation_module/SUMO/projects/regions/data/regions.sumocfg")