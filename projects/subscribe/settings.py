import os
import json

class Settings(object):

	#reward list didnt reset after 
	

	default = os.path.abspath('./../') #default is E:\Python\sumo-windows10\projects
	sumo_config = os.path.join(default, "grid4/data/grid4.sumocfg")
	#sumo_config = os.path.join(default, "Haines_City/data/100/Haines_City.100.sumocfg")
	#sumo_config = os.path.join(default, "london-seg4/data/100/london-seg4.100.100.sumocfg")
	#sumo_config = os.path.join(default, "orlando/orlando-seg1.1000/orlando-seg1.1000.sumocfg")

	sim_save_path = os.path.join(default, "subscribe/simulations")
	sim_save = os.path.join(default, "subscribe/simulations/recent.sim")
	plot_path = os.path.join(default, "subscribe/simulations/plots")

	def __init__(self):

		#test params for getting result from simulation

		self.car_numbers = 10  #set the random amount to spawn when no prev defined cars
		self.simulation_delay = 1 #delay for visualization, 0 runs fast
		self.game_theory_algorithm = ['gta', 'greedy','random', 'base'] #gta, greedy, base, random
		#self.game_theory_algorithm = ['base']
		self.destination = '0_2' #'random' #set to 0 row and 0 column, can be set to 'random'
		#self.destination = '8_34'
		#self.destination = '0_3'
		#self.destination= '0_0'
		self.theta_random = 2000  #used in softmax to determine prob, higher this value the less random it is
		self.simulation_steps = 50 #how many times to repeat simulation

		self.player_capacity_random = (10, 5) #mean,std for capacity
		self.reward_value_random = (10, 5) #mean, std for reward
		
		
		self.reward_amount = 1000
		self.reward_position_std = 30

		self.percent_reward_dist = None #can choose percentage of total cells in the cluster that will contain reward

		self.max_memory_size = 3 #3 conseqtive. how many max nodes store in player memory, these cells are not in the reward consideration list
		#thus when cells is NONE resort to weighted random which uses the gloabal cov cells to determine which weight to choose



class GraphSetting(Settings):
	car_numbers = 1
	reward_numbers= 1
	destination='gneJ49'
	player_reward_random = (50, 5)
	#sim_edge_info_path = os.path.join(self.default, "london-seg3.100/speedhist/edges.stats.csv")





if __name__ == "__main__":
	pass

