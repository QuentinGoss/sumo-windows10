import os
import json

class Settings(object):
	default = os.path.abspath('./../')
	sumo_config = os.path.join(default, "grid4/data/grid4.sumocfg")
	#sumo_config = os.path.join(default, "Haines_City/data/100/Haines_City.100.sumocfg")

	sim_config_load_path = None

	sim_save_path = os.path.join(default, "subscribe/simulations")
	sim_save = os.path.join(default, "subscribe/simulations/recent.sim")
	plot_path = os.path.join(default, "subscribe/simulations/plots")

	row = 121
	column = 82
	
	car_numbers = 100  #set the random amount to spawn when no prev defined cars
	simulation_delay = 0 #delay for visualization, 0 runs fast
	game_theory_algorithm =True #enable and disable game_theory algorithm for comparision
	destination = 'random' #'random' #set to 0 row and 0 column, can be set to 'random'
	theta_random = 1000  #used in softmax to determine prob, higher this value the less random it is
	simulation_steps = 50 #how many times to repeat simulation
	player_reward_random = (50, 5) #mean,std

	#test params for getting result from simulation
	player_list = None
	reward_list = None
	reward_amount = 1000
	reward_distribution_center = [(0,0),(0,column),(row, 0),(row, column)]
	reward_value_std = 10
	reward_position_std = 10
	reward_value_mean = 10





	@classmethod
	def change(cls, player_list, reward_list):
		cls.player_list = player_list
		cls.reward_list = reward_list



class GraphSetting(Settings):
	edge_speed_std = 0.5 #standard deviation for edge
	destination='gneJ49'





if __name__ == "__main__":
	pass

