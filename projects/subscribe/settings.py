import os
class Settings(object):
	default = os.path.abspath('./../')
	map_path = os.path.join(default, "grid4/data/grid4.net.xml")
	radius = 100 #searching around 100miles out
	sumo_config = os.path.join(default, "grid4/data/grid4.sumocfg")
	car_numbers = 10
