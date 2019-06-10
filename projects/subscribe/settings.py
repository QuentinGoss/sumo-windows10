import os
class Settings(object):
	default = os.path.abspath('./../')
	map_path = os.path.join(default, "grid4/data/grid4.net.xml")
	radius = 100 #searching around 100miles out
	sumo_config = os.path.join(default, "grid4/data/grid4.sumocfg")
	car_numbers = 10  #set the random amount to spawn when no prev defined cars
	simulation_delay = 1 #delay for visualization, 0 runs fast
	game_theory_algorithm = False #enable and disable game_theory algorithm for comparision
	destination = '0_0' #'random' #set to 0 row and 0 column, can be set to 'random'
	weight_random_difference = 0.10 #the shortest path are 5+% more likely than other path. max value is 0.125


#feel like the reward should decrease to prevent vehicle backtracking.
#shouldnt the utility consider cost as well? cost can be computed using traci
#weighted random should only consider cells not being traveled before?
#if reward dont decrease maybe the EU matrix should only consider the cells it has not seen yet.