import os
class Settings(object):
	default = os.path.abspath('./../')
	sumo_config = os.path.join(default, "grid5/data/grid5.sumocfg")

	sim_save = os.path.join(default, "subscribe/simulations/recent.sim")
	plot_path = os.path.join(default, "subscribe/simulations/plots")
	
	car_numbers = 10  #set the random amount to spawn when no prev defined cars
	simulation_delay = 0 #delay for visualization, 0 runs fast
	game_theory_algorithm =True #enable and disable game_theory algorithm for comparision
	destination = '0_0' #'random' #set to 0 row and 0 column, can be set to 'random'
	theta_random = 1000  #uses softmax to determine prob, higher this value the less random it is
	simulation_steps = 1000 #how many times to repeat simulation
	player_reward_random = (100, 0.1) #mean,std

class GraphSetting(Settings):
	edge_speed_std = 0.5 #standard deviation for edge

		


#feel like the reward should decrease to prevent vehicle backtracking.
#shouldnt the utility consider cost as well? cost can be computed using traci
#weighted random should only consider cells not being traveled before?
#if reward dont decrease maybe the EU matrix should only consider the cells it has not seen yet.
#nned to be able to enable and disable UI