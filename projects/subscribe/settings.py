import os
class Settings(object):
	default = os.path.abspath('./../')
	map_path = os.path.join(default, "grid4/data/grid4.net.xml")
	radius = 100 #searching around 100miles out
	sumo_config = os.path.join(default, "grid4/data/grid4.sumocfg")
	car_numbers = 10  #set the random amount to spawn when no prev defined cars
	simulation_delay = 0 #delay for visualization, 0 runs fast
	game_theory_algorithm = True #enable and disable game_theory algorithm for comparision
	destination = '0_0' #'random' #set to 0 row and 0 column, can be set to 'random'
