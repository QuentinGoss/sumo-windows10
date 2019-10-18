import tkinter as tk
import traci
from _map import Map
from player import GridPlayer
from random import randrange, choice
from settings import Settings
import time
import numpy as np
from scipy.stats import truncnorm
from operator import mul
from functools import reduce
from postprocess import DataCapture, MultiCapture
from math import exp
import pickle
import os
import datetime






class GridWin(tk.Tk):
	def __init__(self, gui=True, testing='budget'):
		super(GridWin, self).__init__()
		traci.start(["sumo", "-c", Settings.sumo_config])

		self.mode='default' #default, reward

		self.testing = testing #if testing budget keep capacity constant, if testing capacity keep budget constant

		self.env_map = Map(Settings.sumo_config)
		
		self.rowcol_to_junction = self.env_map.complex_row_col

		self.row = int(self.env_map.rows)
		self.column = int(self.env_map.columns)

		#self.rowcol_to_junction = self.env_map.row_col(self.row, self.column) #value is the junction id and key is row_col

		self.rowcol_to_junction.update(dict((v, k) for k, v in self.rowcol_to_junction.items()))
		self.player_list = {} #stores location as key, player object as value in list
		self.reward_list = {} #stores location(grid) as key, reward value as value
		self.random_uniform_reward_list = {} #akbas

		self.min_reward = 0 #min reward value


		self.gui = gui



		self.setting = Settings()

		#settings
		self.reward_distribution_center = [(0,0),(0,self.column),(self.row, 0),(self.row, self.column)]



		if gui:
			self.protocol("WM_DELETE_WINDOW", self.on_closing)

			w=self.winfo_screenwidth()
			h=self.winfo_screenheight()
			size = str(int(w/2))+'x'+str(int(h/2))
			#print(size)
			self.geometry(size)

			self.import_frame = tk.Frame(self, bg='green')
			#self.import_frame.pack(expand=True, fill='both')

			self.grid_frame = tk.Frame(self, height=500, width=500, bg='red')
			self.grid_frame.pack(expand=True, fill='both')

			self.control_frame = tk.Frame(self)
			self.control_frame.pack(expand=True, fill='both')


			self.grid_list = [] #store all the buttons in grid
			self.spawn_grid()
			self.control_buttons()
			self.mainloop()
	
			
	def run_sim_no_gui(self, replay=False):
		if (not replay) or self.testing == 'budget':
			for center in self.reward_distribution_center:
				self.generate_reward_spread(center[0], center[1], self.setting.reward_value_random[1], self.setting.reward_position_std, self.setting.reward_amount, mean=self.setting.reward_value_random[0])
				if self.setting.percent_reward_dist:
					#if we deicided to spread reward based off percentage, only need to do it once over the entire map
					break

		self.simulation(replay=replay)
		if self.testing == 'budget':
			#reset reward list if testing budget. testing budget means change budget values thus change the spread of reward every after every simulation
			self.reward_list = {}



	def default_mode(self):
		#each grid click spawns 1 vehicle, cells black
		#right click undo

		for i in range(self.row):
			for j in range(self.column):
				string_key = str(i) + '_' + str(j)

				self.grid_list[i][j].unbind('<Enter>')
				self.grid_list[i][j].unbind('<Leave>')
				self.grid_list[i][j].unbind('<MouseWheel>')

				if string_key in self.player_list:
					self.grid_list[i][j].configure(bg='black')
					self.grid_list[i][j].configure(text=str(len(self.player_list[string_key])))
				else:
					self.grid_list[i][j].configure(bg=self.default_button_color)
					self.grid_list[i][j].configure(text='')




				self.grid_list[i][j].configure(command = lambda i=i, j=j: self.add_player(i, j))
				self.grid_list[i][j].bind('<Button-3>', lambda event, a=i, b=j, color=self.default_button_color: self.remove_player(a, b, color))
				self.grid_list[i][j].bind('<Button-2>', lambda event, a=i, b=j: self.normal_distribute_players(a,b))
				self.grid_list[i][j].configure(fg='white')


	def ncr(self, n, r):
		r = min(r, n-r)
		numer = reduce(mul, range(n, n-r, -1), 1)
		denom = reduce(mul, range(1, r+1), 1)
		return (numer / denom)


	
	def spawn_reward_mode(self):
		if self.mode == 'default':
			self.mode='reward'
			self.select_rewards.configure(text='Select Vehicles')


			for i in range(self.row):
				for j in range(self.column):
					string_key = str(i) + '_' + str(j)
					self.grid_list[i][j].configure(command=lambda i=i, j=j: self.add_reward(i,j, 1))
					self.grid_list[i][j].configure(bg=self.default_button_color)
					self.grid_list[i][j].configure(fg='black')
					if string_key in self.reward_list:
						self.grid_list[i][j].configure(text=str(self.reward_list[string_key]))
					else:
						self.grid_list[i][j].configure(text='0')

					self.grid_list[i][j].bind('<Button-2>', lambda event, a=i, b=j: self.normal_distribute_players(a,b, False))

					self.grid_list[i][j].bind('<Enter>', lambda event, i=i, j=j: self.grid_list[i][j].bind('<MouseWheel>', lambda event, i=i, j=j:self.add_reward(i,j, int(event.delta/120))))#       self.reward_change(event, i, j)))
					self.grid_list[i][j].bind('<Leave>', lambda event: self.grid_list[i][j].unbind('<MouseWheel>'))
					self.grid_list[i][j].bind('<Button-3>', lambda event, i=i, j=j: self.reward_remove(i,j)) #this button used to clear rewards

		else:
			self.default_mode()
			self.mode='default'
			self.select_rewards.configure(text='Select Rewards')


	def reward_remove(self, row, column):
		string_key = str(row) + '_' + str(column)
		try:
			del self.reward_list[string_key]
			if self.gui:
				self.grid_list[row][column].configure(text='0')
		except KeyError:
			print('no rewards at this cell')


	def add_reward(self, row, column, scroll_value):
		string_key = str(row) + '_' + str(column)
		if string_key in self.reward_list:
			self.reward_list[string_key] += scroll_value
		else:
			self.reward_list[string_key] = scroll_value

		if self.reward_list[string_key] < 0:
			self.reward_list[string_key]=0


		if self.min_reward == 0 or (self.reward_list[string_key] < self.min_reward):
			self.min_reward = self.reward_list[string_key]
			print(f'min reward value is {self.min_reward} at location {string_key}')
		


		if self.gui:
			self.grid_list[row][column].configure(text=str(self.reward_list[string_key]))





	def normal_distribute_players(self, a,b, dist_player=True):
		second_level = tk.Toplevel(self)
		second_level.title('normal distribution')

		std_label = tk.Label(second_level, text='STD: ').grid(row=0, column=0)
		number_label = tk.Label(second_level, text='Amount: ').grid(row=1, column=0)

		std_var = tk.StringVar()
		num_var = tk.StringVar()

		L1 = tk.Entry(second_level, justify='left', relief='ridge', background='#6699ff',textvariable=std_var)
		L1.grid(row=0, column=1)

		L2 = tk.Entry(second_level, justify='left', relief='ridge', background='#6699ff', textvariable=num_var)
		L2.grid(row=1, column=1)

		enter_button = tk.Button(second_level,text='Enter', command=lambda a=a, b=b, second_level=second_level,std=std_var, num_veh=num_var, dist_player=dist_player:self.generate_players(a,b, second_level ,std, num_var, dist_player))
		enter_button.grid(row=2, column=0)
		second_level.bind('<Return>', lambda event, a=a, b=b, second_level=second_level,std=std_var, num_veh=num_var:self.generate_players(a,b, second_level ,std, num_var))

	def generate_players(self, a,b, root, std=None, num_var=None, dist_player=True):
		if std and num_var:
			std_value = float(std.get())
			num_var_value = int(num_var.get())
		else:
			print('no std and number chosen')
			#randomly generate
		x = self.get_truncated_normal(a, std_value, 0, 10).rvs(num_var_value+10000).round().astype(int)
		y = self.get_truncated_normal(b, std_value, 0, 10).rvs(num_var_value+10000).round().astype(int)		


		xPo = np.random.choice(x, num_var_value)
		yPo = np.random.choice(y, num_var_value)

		for x_points, y_points in zip(xPo, yPo):

			if dist_player:
				self.add_player(x_points, y_points)

			else:
				self.add_reward(x_points, y_points, 1)

		root.destroy()

	def generate_reward_spread(self, x, y, value_std, position_std, amount, mean=None):

		if self.setting.percent_reward_dist:
			print(f'length is {len(self.reward_list)}')
			#if defined percentage is true then spread reward based off the percentage value randomly over the map
			junction_list = np.array(list(self.env_map.junctions.keys()))
			choice_junctions = [self.rowcol_to_junction[x] for x in np.random.choice(junction_list, int(len(junction_list)*self.setting.percent_reward_dist), replace=False)]
			for junct_grid in choice_junctions:
				row, column = int(junct_grid.split('_')[0]), int(junct_grid.split('_')[1])
				if mean:
					mean_dist = self.get_truncated_normal(mean, value_std, 0, 10*value_std*mean).rvs(amount+10000).astype(float)
					self.add_reward(row, column, np.random.choice(mean_dist, 1)[0])

			assert len(self.reward_list) <= len(junction_list), f'Error reward list greater than junction'

			assert len(self.reward_list) == int(len(junction_list)*self.setting.percent_reward_dist), f'Error reward and expcted per not match expected {int(len(junction_list)*self.setting.percent_reward_dist)}, got {len(self.reward_list)} chocie {len(choice_junctions)}'
			return


		#if mean is not none generate distribution based off mean to add to rewards
		x, y = self.find_closest_road(x, y)

		x_dist = self.get_truncated_normal(x, position_std, 0, self.row).rvs(amount+10000).round().astype(int)
		y_dist = self.get_truncated_normal(y, position_std, 0, self.column).rvs(amount+10000).round().astype(int)
		

		xPo = np.random.choice(x_dist, amount)
		yPo = np.random.choice(y_dist, amount)
		
		zip_po = list(zip(xPo, yPo))

		i = 0
		while i < len(zip_po):
			x_points, y_points = zip_po[i]
			string_key = str(x_points) + '_' + str(y_points)
			if not string_key in self.rowcol_to_junction:
				#print(string_key, 'not in')
				zip_po[i] = (np.random.choice(x_dist, 1)[0], np.random.choice(y_dist, 1)[0])
				continue
			if mean:
				mean_dist = self.get_truncated_normal(mean, value_std, 0, 10*value_std*mean).rvs(amount+10000).astype(float)
				self.add_reward(x_points, y_points, np.random.choice(mean_dist, 1)[0])
			else:
				self.add_reward(x_points, y_points, 1)
			i+=1

		#assert len(self.reward_list) == amount, f'len of rewrd amount does not match {len(self.reward_list)}'
	
	def find_closest_road(self, x, y):
		closest = None
		for key, value in self.env_map.junctions.items():
			key = self.rowcol_to_junction[key]
			x1, y1 = int(key.split('_')[0]), int(key.split('_')[1])
			dist = np.linalg.norm(np.array([x,y])-np.array([x1, y1]))
			if not closest:
				closest = (key, dist)
			else:
				if dist < closest[1]:
					closest = (key, dist)

		return int(closest[0].split('_')[0]), int(closest[0].split('_')[1])



	def get_truncated_normal(self, mean=0, sd=1, low=0, upp=10):
		return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

	def control_buttons(self):
		for row in range(2):
			for column in range(3):
				self.control_frame.grid_columnconfigure(column, weight=1)
				self.control_frame.grid_rowconfigure(row, weight=1)

		start_sim_button = tk.Button(self.control_frame, text='START', command=self.simulation)
		start_sim_button.grid(row=0, column=1, sticky=tk.N+tk.S+tk.W+tk.E)


		self.select_rewards = tk.Button(self.control_frame, text='Select Rewards', command = self.spawn_reward_mode)
		self.select_rewards.grid(row=0, column=0, sticky=tk.N+tk.S+tk.W+tk.E)

		clear_button = tk.Button(self.control_frame, text='CLEAR', command=self.clear)
		clear_button.grid(row=0, column=2,sticky=tk.N+tk.S+tk.W+tk.E)

		self.replay_button = tk.Button(self.control_frame, text='Replay Simulation', command=self.replay_simulation)
		self.replay_button.grid(row=1, column=1,sticky=tk.N+tk.S+tk.W+tk.E)

		self.save_button = tk.Button(self.control_frame, text='Save Simulation', command=self.save_simulation)
		self.save_button.grid(row=1, column=0,sticky=tk.N+tk.S+tk.W+tk.E)

		self.load_button = tk.Button(self.control_frame, text='Load Simulation', command=self.load_simulation)
		self.load_button.grid(row=1, column=2,sticky=tk.N+tk.S+tk.W+tk.E)


	def load_simulation(self):
		with open(Settings.sim_save, 'rb') as config_dictionary_file:
			self.cap = pickle.load(config_dictionary_file)
		print('simulation load sucess...')
		self.replay_simulation(load=True)


	def replay_simulation(self, algo, load=False):
		print('player numbers total(10):',len(self.cap.player_list))
		for value in self.cap.player_list:
			new_player = GridPlayer(value.start, value.destination)
			row, column = self.rowcol_to_junction[value.start].split('_')
			if load:
				new_player.node_path = value.node_hit
				self.add_player(int(row), int(column), new_player)
			else:
				self.add_player(int(row), int(column))

		self.cap.player_list=[]

		return self.start_sim(algo=algo, replay=True, load=load)


	def save_simulation(self):
		if not self.cap:
			print('No recent simulation, please run sim before save')
			return
		with open(Settings.sim_save, 'wb') as config_dictionary_file:
			pickle.dump(self.cap, config_dictionary_file)
		print('simulation saved success...')

	def spawn_grid(self):
		for i in range(self.row):
			temp_list = []
			for j in range(self.column):
				b= tk.Button(self.grid_frame)
				b.grid(row=i, column=j, sticky=tk.N+tk.S+tk.W+tk.E, columnspan=1)
				self.default_button_color = b.cget('bg')
				self.grid_frame.grid_columnconfigure(j, weight=2)
				self.grid_frame.grid_rowconfigure(i, weight=2)
				temp_list.append(b)
			self.grid_list.append(temp_list)
		self.default_mode()


	def find_adjacent_cells(self, x_y, param='to'): #this function need to change to be determined using sumo
		adjacent_list_sumo = [self.rowcol_to_junction[x] for x in self.env_map.find_adjacent_cells(self.rowcol_to_junction[x_y], param=param)]
		return adjacent_list_sumo



	def find_adjacent_players(self, x_y):
		player_num = 0
		adjacent_list = self.find_adjacent_cells(x_y, param='from')
		for value in adjacent_list:
			
			try:
				player_num +=len(self.player_list[value])
			except KeyError:
				continue
		return player_num

	def remove_player(self, row, column, color):

		try:

			string_key = str(row) + '_' + str(column)	
			if len(self.player_list[string_key]) == 1:
				del self.player_list[string_key]
			else:
				self.player_list[string_key].pop(0)

			
			self.env_map.junctions[self.rowcol_to_junction[string_key]].number_players -= 1
			

			if self.env_map.junctions[self.rowcol_to_junction[string_key]].number_players == 0:
				self.grid_list[row][column].configure(text='')
				self.grid_list[row][column].configure(bg=color)
			else:
				self.grid_list[row][column].configure(text=self.env_map.junctions[self.rowcol_to_junction[string_key]].number_players)



		except KeyError:
			#try to delete  vehicle that doesnt exist
			pass


	def add_player(self, row, column, player=None): # add player to dictionary and return a dict
		string_key = str(row) + '_' + str(column)


		destination = self.setting.destination
		if destination =='random':
			destination = str(randrange(self.row))+'_'+str(randrange(self.column))

		if string_key == destination:
			print('start is destination')
			return False

		try:	
			if player:
				player_instance = player
			else:
				player_instance = GridPlayer(self.rowcol_to_junction[string_key], self.rowcol_to_junction[destination])
				player_instance.path = self.env_map.find_best_route(player_instance.start, player_instance.destination)
				if not (player_instance.path and player_instance.path.edges):
					print('no path edges')
					return False
				player_instance.node_path = [self.env_map.edges[x]._to for x in player_instance.path.edges]

			player_instance.capacity = self.get_truncated_normal(self.setting.player_capacity_random[0], self.setting.player_capacity_random[1], 0, self.setting.player_capacity_random[0]*2).rvs(1)[0]
			#print('plyer capacity is: ', player_instance.capacity)
		except KeyError as e:
			print(f'no key in dict {e}')
			return False

		print(f'vehicle start at {string_key} end at {destination} capacity value is {player_instance.capacity}, reward list len is {len(self.reward_list)}')


		if string_key in self.player_list:
			self.player_list[string_key].append(player_instance)
		else:
			self.player_list[string_key] = [player_instance]


		self.env_map.junctions[self.rowcol_to_junction[string_key]].number_players += 1

		if self.gui:


			self.grid_list[row][column].configure(bg='black')
			self.grid_list[row][column].configure(text=self.env_map.junctions[self.rowcol_to_junction[string_key]].number_players)
		return True


	def redirect_route(self, player_instance, new_route):
		if new_route[0] != player_instance.destination:
			player_instance.path = new_route # self.env_map.find_best_route(next_node, player_instance.destination)
			player_instance.node_path = [self.env_map.edges[x]._to for x in player_instance.path.edges]
			player_instance.node_index=0

		return player_instance

	def compute_sensing_plan(self, player_amount, reward, cost):
		return ((player_amount-1)*reward)/((player_amount**2)*cost)



	def GTA_next_node(self, location, player_instance, current_node):
		#takes in location, player, and next node return new next node and player instance
		cells = self.find_adjacent_cells(location) #return grid junction
		assert cells, f'Junction has no where else to go {location}'

		new_route = player_instance.path

		#print('new route is ', new_route)

		max_utility = 0
		max_utility_cell = None

		for cell in cells:
			#print(f'cells value is {cells}')

			adjacent_players = self.find_adjacent_players(cell)
			assert adjacent_players > 0, f'player is {adjacent_players} failed, location: {location}, surrounding cells: {cells}, current: {cell}, player: {self.player_list[location]}'

			cell_utility = 0  #total utility at that cell 
			try:
				cell_utility = self.reward_list[cell]
				if cell_utility == 0:
					continue
			except KeyError:
				continue

			expected_utility = 0
			expected_sensing_plan = 0


			if adjacent_players == 1: #no one is around me
				expected_utility = cell_utility
				expected_sensing_plan = self.env_map.junctions[self.rowcol_to_junction[cell]].cost
			else:
				#sum the denomenator of the combination, store ncr in list to reuse later
				ncr_list = [self.ncr(adjacent_players-1, player_number) for player_number in range(0, adjacent_players)] #consists of a list from 0
				denom = reduce(lambda x,y: x+y, ncr_list) #from 0 to second to last in list

				for current_player in range(1, adjacent_players+1):
					numerator = ncr_list[current_player-1] #retrieve ncr value from list
					prM = numerator/denom
					expected_utility += (prM*(cell_utility/pow(current_player, 2)))
					expected_sensing_plan += (prM*(self.compute_sensing_plan(current_player, self.reward_list[cell], self.env_map.junctions[self.rowcol_to_junction[cell]].cost)))




			if (expected_utility > max_utility) and (expected_sensing_plan <= player_instance.capacity):# and (not cell in player_instance.past_recent_nodes):
				#choose highest utility, with capacity taken into consideration, as well as no repeating within last 3 visited
				max_utility = expected_utility
				max_utility_cell = cell


		#this part to generate the weighted random path

		if not max_utility_cell:
			#if adj cells no rewards
			#if adj cells rewards dont fit capacity
			#weighted random need to priotize coverage good
			weight_dict, best_route = self.env_map.find_best_route(current_node, player_instance.destination, weights=True)
			#weight_dict = {key:value.travelTime*self.visited_cell_list[key]*len(value.edges) if key in self.visited_cell_list else value.travelTime for key, value in weight_dict.items()}
			#travel time multiple by cell visited number , multiple by number of edges before reaching destination



			try:
				total_sum = reduce(lambda x,y:x+y,[exp(self.setting.theta_random/x.travelTime) for x in weight_dict.values()])
				prob_distribute = [exp(self.setting.theta_random/x.travelTime)/total_sum for x in weight_dict.values()]

				selected_index = np.random.choice(len(cells), 1, p=prob_distribute)
				next_node = list(weight_dict.keys())[selected_index[0]]

			except OverflowError:
				#when theta random value is too large just take the best route node
				next_node = self.env_map.edges[best_route.edges[0]]._to



		else:
			#when max utility cells is found its in terms of grid junction need to convert to sumo junction
			next_node = self.rowcol_to_junction[max_utility_cell]


		player_instance = self.redirect_route(player_instance, new_route)

		if len(player_instance.past_recent_nodes) < self.setting.max_memory_size:
			player_instance.past_recent_nodes.append(self.rowcol_to_junction[next_node]) #sumo junction is added to memory
		else:
			player_instance.past_recent_nodes.pop(0)
			player_instance.past_recent_nodes.append(self.rowcol_to_junction[next_node])

		return next_node, player_instance


	def simulation(self, replay=False):
		for algo in self.setting.game_theory_algorithm:
			multi_data = MultiCapture('Traffic Simulation')
			i=0
			while i < self.setting.simulation_steps:
				print('iteration ', i)
				if replay:
					suc = self.replay_simulation(algo=algo)
				else:
					suc = self.start_sim(algo=algo) #first time running simulation generate random players save it to self.cap
					replay=True



				if suc: #if simulation is success
					self.cap.setting = self.setting
					self.cap.reward_list = self.reward_list
					self.cap.reward_junction_ratio = len(self.reward_list)/len(self.env_map.junctions)
					cov = self.cap.calculate_coverage()
					test_cov = self.cap.calculate_test_coverage()
					print('road utilization is ', cov)
					print('coverage is ', test_cov)
					multi_data.simulation_conv_list.append(cov)
					multi_data.simulation_test_coverage.append(test_cov)
					multi_data.simulation_list.append(self.cap)
					
					#if i%10 ==0:
					if i == (self.setting.simulation_steps-1):
						if self.setting.percent_reward_dist:
							multi_data.pickle_save(os.path.join(Settings.sim_save_path, f'{self.setting.percent_reward_dist}_reward{self.setting.reward_value_random[0]}_capacity{self.setting.player_capacity_random[0]}_Step{self.setting.simulation_steps}_{algo}_cluster_reward.sim'))
						else:
							multi_data.pickle_save(os.path.join(Settings.sim_save_path, f'reward{self.setting.reward_value_random[0]}_capacity{self.setting.player_capacity_random[0]}_Step{self.setting.simulation_steps}_{algo}_cluster_reward.sim'))
					i+=1
				
				self.player_list = {}
			#changing rewards should be before this funtion
			
			

			if self.testing =='budget' and not self.setting.percent_reward_dist:  #when running budget distribute based off percentage no need to run it second time
				temp_multi_data = MultiCapture('Traffic Simulation')
				temp = self.reward_list #save the temp reward list before replacing it with uniform reward.

				j = 0
				while j < self.setting.simulation_steps:
					#this is for random uniform reward distribution
					self.reward_spread_uniform((multi_data.simulation_list[0].reward_junction_ratio)*len(self.env_map.junctions))
					suc = self.replay_simulation(algo=algo)
					if suc:
						cov = self.cap.calculate_coverage()
						test_cov = self.cap.calculate_test_coverage()
						print('RU for random reward ', cov)
						print('COV for random reward ', test_cov)
						temp_multi_data.simulation_conv_list.append(cov)
						temp_multi_data.simulation_test_coverage.append(test_cov)
						temp_multi_data.simulation_list.append(self.cap)
						if j == (self.setting.simulation_steps-1):
							temp_multi_data.pickle_save(os.path.join(Settings.sim_save_path, f'reward{self.setting.reward_value_random[0]}_capacity{self.setting.player_capacity_random[0]}_Step{self.setting.simulation_steps}_{algo}_random_reward.sim'))	
						j+=1

					self.player_list = {}


				self.reward_list = temp

		
	def reward_spread_uniform(self, amount_rewards):
		#spread rewards uniformly based of ratio
		self.reward_list = {}

		if self.random_uniform_reward_list:
			for key, value in self.random_uniform_reward_list.items():
				self.random_uniform_reward_list[key] = randrange(self.setting.reward_value_random[0]-self.setting.reward_value_random[1], self.setting.reward_value_random[0]+self.setting.reward_value_random[1])

			self.reward_list = self.random_uniform_reward_list
		else:

			reward_locations = np.random.choice(list(self.env_map.junctions.keys()), round(amount_rewards))
			for value in reward_locations:
				value = self.rowcol_to_junction[value]
				x,y = int(value.split('_')[0]), int(value.split('_')[1])
				self.add_reward(x,y,randrange(self.setting.reward_value_random[0]-self.setting.reward_value_random[1], self.setting.reward_value_random[0]+self.setting.reward_value_random[1]))



	def greedy_next_node(self, location, player_instance, current_node):
		'''
		location current location in terms of sumo
		player instance the player we are looking at
		current node is the location in terms of grid values
		next_node is predicted next node based on dex
		'''

		shortest_path = False
		cells = self.find_adjacent_cells(location)

		#cells return grid location not sumo location
		#reward list returns grid location as well


		max_utility_cell = None
		max_utility = 0
		for cell in cells:
			try:
				self.reward_list[cell]
				if not max_utility_cell and (self.reward_list[cell]<=player_instance.capacity):
					max_utility_cell = cell
					max_utility = self.reward_list[cell]
				else:
					if (self.reward_list[cell] > max_utility) and (self.reward_list[cell]<=player_instance.capacity):
						max_utility_cell = cell
						max_utility = self.reward_list[cell]
			except KeyError as e:
				pass

		#two cases, when no rewards around, or 
		#find smallest reward, if capacity falls below smallest reward, uses djk instead
		if not max_utility_cell:

			#let random jump decide on capacity that way greedy no need to implement
			next_node, player_instance, shortest_path = self.random_next_node(location, player_instance, current_node) #remove random directly go towards destination shortest path
			#next node for random returns sumo cells
		else:
			next_node = max_utility_cell

			assert max_utility_cell in self.reward_list, f'something is wrong {max_utility_cell} supose in reward list'

			player_instance.collected_sp_list.append(next_node)

			#next node normally return grid cells

			next_node = self.rowcol_to_junction[next_node]
			player_instance.capacity -= max_utility
				


		return next_node, player_instance, shortest_path






	def random_next_node(self, location, player_instance, current_node):
		# capacity for random
		shortest_path = False
		cells = self.find_adjacent_cells(location)
		weight_dict, best_route = self.env_map.find_best_route(current_node, player_instance.destination, weights=True)
		try:
			total_sum = reduce(lambda x,y:x+y,[exp(self.setting.theta_random/x.travelTime) for x in weight_dict.values()])
			prob_distribute = [exp(self.setting.theta_random/x.travelTime)/total_sum for x in weight_dict.values()]

			#print('prob_distribute ', prob_distribute)
			#print('max value is {}, index value is {}, the next cell is {}, current cell is {}'.format(max(prob_distribute), prob_distribute.index(max(prob_distribute)), self.rowcol_to_junction[list(weight_dict.keys())[prob_distribute.index(max(prob_distribute))]], self.rowcol_to_junction[current_node]))
			selected_index = np.random.choice(len(cells), 1, p=prob_distribute)
			next_node = list(weight_dict.keys())[selected_index[0]]

		except OverflowError:
			#when theta random value is too large just take the best route node
			next_node = self.env_map.edges[best_route.edges[0]]._to

		if self.rowcol_to_junction[next_node] in self.reward_list: #if next node contains rewards
			if self.reward_list[self.rowcol_to_junction[next_node]] <= player_instance.capacity: #if reward is less than capacity then collect
				player_instance.collected_sp_list.append(self.rowcol_to_junction[next_node])
				player_instance.capacity -= self.reward_list[self.rowcol_to_junction[next_node]]
			else: #cant collect due to capacity
				if player_instance.capacity < self.min_reward: #check is player capacity less than min reward on map
					shortest_path = True
					player_instance.path = self.env_map.find_best_route(current_node, player_instance.destination)
					player_instance.node_path = [self.env_map.edges[x]._to for x in player_instance.path.edges]
					player_instance.node_index = 0 #reset path info
					#need to reset player path setting index =0




		return next_node, player_instance, shortest_path




	def start_sim(self, algo, replay=False, load=False):
		temp_reward = self.reward_list

		shortest_path = False

		#print('len reward is ', len(self.reward_list))

		#simulation start
		if self.gui:
			self.default_mode()

		if not replay: self.cap = DataCapture(len(self.env_map.junctions), self.rowcol_to_junction) #reset if its not replay

		#if no predefined players, randomly spawn players
		if not self.player_list:
			i = 0
			while i < self.setting.car_numbers:
				row_col = choice(list(self.env_map.junctions.keys()))
				row, column = self.rowcol_to_junction[row_col].split('_')[0], self.rowcol_to_junction[row_col].split('_')[1]
				suc = self.add_player(row, column)
				if suc:
					i +=1
					print(f'player added to {row}, {column}')
				else:
					print(f'failed to add player at {row}, {column}')



		arrived_locations = [] #destinations of all vehicles to reset after
					

		while self.player_list:
			player_left = 0

			if self.gui:
				self.update()
				time.sleep(self.setting.simulation_delay)
			temp_dict = {}
			for location, players in self.player_list.items():
				for i, player in enumerate(players):

					player_left+=1

					
					#junction value in sumo

					#insert logic for game theory, 
					if algo=='gta' and not load: #if its loading from file then just play players
						next_node, player = self.GTA_next_node(location, player, self.rowcol_to_junction[location])




					elif algo=='greedy' and not load:
						#run greedy algo, only go towards highest rewards. check capacity and reduce capacity based on reward value else result in infinite loop
						if not shortest_path:
							next_node, player, shortest_path = self.greedy_next_node(location, player, self.rowcol_to_junction[location])

						if shortest_path:
							print('player taking shortest path in greedy')
							next_node = player.get_next()

					elif algo=='random' and not load:
						if not shortest_path:
							next_node, player, shortest_path = self.random_next_node(location, player, self.rowcol_to_junction[location])
						
						if shortest_path:
							print('player taking shortest path in random')
							next_node = player.get_next()


					elif algo == 'base' and not load:
						next_node = player.get_next()
						if self.rowcol_to_junction[next_node] in self.reward_list:
							if self.reward_list[self.rowcol_to_junction[next_node]] <= player.capacity:
								player.collected_sp_list.append(self.rowcol_to_junction[next_node])
								player.capacity -= self.reward_list[self.rowcol_to_junction[next_node]]




					player.node_hit.append(next_node) # for post processing
					player.reward_hit.append(player.capacity) # for post processing

					button_name = self.rowcol_to_junction[next_node]
					
					button_row, button_column = button_name.split('_')

					if next_node == player.destination:
						print(f'player has arrived to {self.rowcol_to_junction[player.destination]} from {self.rowcol_to_junction[player.start]} nodes traveled:{len(player.node_hit)}')
						arrived_locations.append(player.destination)
						self.cap.player_list.append(player) #add player to the post processing list

					else:
						#if final destination is not reached add it to the temp dict

						if button_name in temp_dict:
							temp_dict[button_name].append(player)
						else:
							temp_dict[button_name] = [player]
					
					self.env_map.junctions[self.rowcol_to_junction[button_name]].number_players += 1
					self.env_map.junctions[self.rowcol_to_junction[location]].number_players -= 1

					if self.gui:
						self.grid_list[int(button_row)][int(button_column)].configure(bg='black')
						self.grid_list[int(button_row)][int(button_column)].configure(text=self.env_map.junctions[self.rowcol_to_junction[button_name]].number_players)


				#every time a player move away check if the edge contains more players
				player_number = self.env_map.junctions[self.rowcol_to_junction[location]].number_players
				prev_button_row, prev_button_column = location.split('_')

				if self.gui:
					if player_number == 0:
						self.grid_list[int(prev_button_row)][int(prev_button_column)].configure(bg='white')
					else:
						self.grid_list[int(prev_button_row)][int(prev_button_column)].configure(text=player_number)


			self.player_list = temp_dict

			print(f'{player_left} remaining')

			#if capactiy too low make random jumps towards destination

			if algo=='gta': #reduce capacity based on sensing plan

				for location, players in self.player_list.items():
					print('location is ', location)

					location_cost = self.env_map.junctions[self.rowcol_to_junction[location]].cost
					
					

					for i, player in enumerate(players):
						try:
							self.player_list[location][i].reward += (self.reward_list[location]/len(self.player_list[location])) #question mark.. if location no reward dont calculate sensing plan
							player_sensing_plan = self.compute_sensing_plan(len(self.player_list[location]), self.reward_list[location], location_cost)
							
							#whats the default expected sensing plan when there is only 1 player?? 
							if self.reward_list[location] != 0:
								# if you arrived and your cost is more than your player capacity might as well take what ever your capacity can handle
								if player_sensing_plan <= player.capacity:
									if player_sensing_plan ==0: #calculated sensing plan equal to 0
										if location_cost > player.capacity:
											player_sensing_plan = player.capacity
										else:
											player_sensing_plan = location_cost

									if player.capacity > 0:
										self.player_list[location][i].collected_sp_list.append(location)
										self.player_list[location][i].capacity -= player_sensing_plan

									if self.player_list[location][i].capacity < 0: 
										self.player_list[location][i].capacity = 0
							
						

						except KeyError as e:
							continue
			else:
				pass
	



	
		print('simulation completed')
		self.reset_junction_players(arrived_locations)
		self.reward_list = temp_reward
		return True


	def clear(self):
		if self.mode == 'default':
			self.player_list = {}
			self.default_mode()
		else:
			self.mode='default'
			self.reward_list = {}
			self.spawn_reward_mode()


	def reset_junction_players(self, arrived_locations):
		for value in set(arrived_locations):
			self.env_map.junctions[value].number_players = 0
		

	def on_closing(self):
		self.destroy()
		traci.close()


if __name__ == "__main__":

	cap_value=None
	

	root = GridWin(gui=False, testing='capacity') #testing budget keep caapcity same

	for i in range(5):
		#print('im here ', i)
		if not cap_value:
			#print('root value 1', root.player_capacity_random)
			root.run_sim_no_gui() #this one needs fix
			cap_value = root.cap
		else:
			#print('root value not 1', root.player_capacity_random)
			root.cap = cap_value  #use previous cap value
			root.run_sim_no_gui(replay=True)
			#reaply simulation needs to run multiple simulations
		root.setting.player_capacity_random = (root.setting.player_capacity_random[0] + 40, 5)
		#root.setting.reward_value_random = (root.setting.reward_value_random[0] + 40, 5)
		#root.setting.percent_reward_dist += 0.2


	root.on_closing()
