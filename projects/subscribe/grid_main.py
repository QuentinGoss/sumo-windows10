import tkinter as tk
import traci
from _map import Map
from player import GridPlayer
from random import randrange
from settings import Settings
import time
import numpy as np
from scipy.stats import truncnorm
from operator import mul
from functools import reduce
from postprocess import DataCapture


row = 11
column = 11

mode='default' #default, reward



class GridWin(tk.Tk):
	def __init__(self, row, column):
		super(GridWin, self).__init__()
		traci.start(["sumo", "-c", Settings.sumo_config])


		self.cap = DataCapture(row, column)

		w=self.winfo_screenwidth()
		h=self.winfo_screenheight()
		size = str(int(w/2))+'x'+str(int(h/2))
		print(size)
		self.geometry(size)

		self.row = row
		self.column = column

		self.import_frame = tk.Frame(self, bg='green')
		self.import_frame.pack(expand=True, fill='both')

		self.grid_frame = tk.Frame(self, height=500, width=500, bg='red')
		self.grid_frame.pack(expand=True, fill='both')

		self.control_frame = tk.Frame(self, height=20, bg='blue')
		self.control_frame.pack(expand=True, fill='both')





			
		self.grid_list = [] #store all the buttons in grid
		self.env_map = Map()
		self.rowcol_to_junction = self.env_map.row_col(self.row, self.column) #value is the junction id and key is row_col
		self.rowcol_to_junction.update(dict((v, k) for k, v in self.rowcol_to_junction.items()))
		self.player_list = {} #stores location as key, player object as value
		self.reward_list = {} #stores location as key, reward value as value



		self.spawn_grid()
		self.control_buttons()


	def default_mode(self):
		#each grid click spawns 1 vehicle, cells black
		#right click undo

		for i in range(row):
			for j in range(column):
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




				self.grid_list[i][j].configure(command = lambda i=i, j=j: self.add_player(i, j, max_num=1))
				self.grid_list[i][j].bind('<Button-3>', lambda event, a=i, b=j, color=self.default_button_color: self.remove_player(a, b, color))
				self.grid_list[i][j].bind('<Button-2>', lambda event, a=i, b=j: self.normal_distribute_players(a,b))
				self.grid_list[i][j].configure(fg='white')


	def ncr(self, n, r):
		r = min(r, n-r)
		numer = reduce(mul, range(n, n-r, -1), 1)
		denom = reduce(mul, range(1, r+1), 1)
		return (numer / denom)


	
	def spawn_reward_mode(self):
		global mode
		if mode == 'default':
			mode='reward'
			self.select_rewards.configure(text='Select Vehicles')


			for i in range(row):
				for j in range(column):
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
			mode='default'
			self.select_rewards.configure(text='Select Rewards')


	def reward_remove(self, row, column):
		string_key = str(row) + '_' + str(column)
		try:
			del self.reward_list[string_key]
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


	def get_truncated_normal(self, mean=0, sd=1, low=0, upp=10):
		return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

	def control_buttons(self):
		start_sim_button = tk.Button(self.control_frame, text='start simulation', command=self.start_sim)
		start_sim_button.pack(expand=True, fill='both')


		self.select_rewards = tk.Button(self.control_frame, text='Select Rewards', command = self.spawn_reward_mode)
		self.select_rewards.pack(expand=True, fill='both')

		clear_button = tk.Button(self.control_frame, text='clear', command=self.clear)
		clear_button.pack(expand=True, fill='both')

	def spawn_grid(self):
		for i in range(row):
			temp_list = []
			for j in range(column):
				b= tk.Button(self.grid_frame)
				b.grid(row=i, column=j, sticky=tk.N+tk.S+tk.W+tk.E, columnspan=1)
				self.default_button_color = b.cget('bg')
				self.grid_frame.grid_columnconfigure(j, weight=2)
				self.grid_frame.grid_rowconfigure(i, weight=2)
				temp_list.append(b)
			self.grid_list.append(temp_list)
		self.default_mode()


	def find_adjacent_cells(self, x_y):
		adjacent_list = []
		button_name = x_y.split('_')
		x, y = int(button_name[0]), int(button_name[1])


		if ('_'.join([str(x+1), str(y+1)])) in self.rowcol_to_junction:
			adjacent_list.append('_'.join([str(x+1), str(y+1)]))


		if ('_'.join([str(x), str(y+1)])) in self.rowcol_to_junction:
			adjacent_list.append('_'.join([str(x), str(y+1)]))


		if ('_'.join([str(x+1), str(y)])) in self.rowcol_to_junction:
			adjacent_list.append('_'.join([str(x+1), str(y)]))

		if ('_'.join([str(x-1), str(y+1)])) in self.rowcol_to_junction:
			adjacent_list.append('_'.join([str(x-1), str(y+1)]))

		if ('_'.join([str(x+1), str(y-1)])) in self.rowcol_to_junction:
			adjacent_list.append('_'.join([str(x+1), str(y-1)]))

		if ('_'.join([str(x-1), str(y-1)])) in self.rowcol_to_junction:
			adjacent_list.append('_'.join([str(x-1), str(y-1)]))


		if ('_'.join([str(x-1), str(y)])) in self.rowcol_to_junction:
			adjacent_list.append('_'.join([str(x-1), str(y)]))

		if ('_'.join([str(x), str(y-1)])) in self.rowcol_to_junction:
			adjacent_list.append('_'.join([str(x), str(y-1)]))

		return adjacent_list

	def find_adjacent_players(self, x_y):
		player_num = 0
		adjacent_list = self.find_adjacent_cells(x_y)
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


	def add_player(self, row, column, max_num=None): # add player to dictionary and return a dict
		string_key = str(row) + '_' + str(column)


		destination = Settings.destination
		if destination =='random':
			destination = str(randrange(self.row))+'_'+str(randrange(self.column))


		player_instance = GridPlayer(self.rowcol_to_junction[string_key], self.rowcol_to_junction[destination])
		if player_instance.start != player_instance.destination:
			player_instance.path = self.env_map.find_best_route(player_instance.start, player_instance.destination)
			player_instance.node_path = [self.env_map.edges[x]._to for x in player_instance.path.edges]


			if string_key in self.player_list:
				self.player_list[string_key].append(player_instance)
			else:
				self.player_list[string_key] = [player_instance]


			self.env_map.junctions[self.rowcol_to_junction[string_key]].number_players += 1

			self.grid_list[row][column].configure(bg='black')
			self.grid_list[row][column].configure(text=self.env_map.junctions[self.rowcol_to_junction[string_key]].number_players)


	def redirect_route(self, location, player_index, next_node, reward):
		player_instance = self.player_list[location][player_index]
		if next_node != player_instance.destination:
			player_instance.path = self.env_map.find_best_route(next_node, player_instance.destination)
			player_instance.node_path = [self.env_map.edges[x]._to for x in player_instance.path.edges]
			player_instance.node_index=0
			player_instance.capacity -= reward

		return player_instance




	def GTA_next_node(self, location, player_index, next_node):
		#takes in the location at the car, the index of the player within the list, and the next default node for the vehicle path
		cells = self.find_adjacent_cells(location)

		player_amount = 0 #need to determine how many players to share the reward with
		max_utility = 0
		max_utility_cell = None

		for cell in cells:
			adjacent_players = self.find_adjacent_players(cell) #in jake's code this should return N-1
			assert adjacent_players > 0, f'player is {adjacent_players} failed'

			cell_utility = 0  #total utility at that cell 
			try:
				cell_utility = self.reward_list[cell]
				if cell_utility == 0:
					continue
			except KeyError:
				continue

			expected_utility = 0

			if adjacent_players <=1:
				expected_utility = cell_utility
			else:
				#sum the denomenator of the combination, store ncr in list to reuse later
				ncr_list = [self.ncr(adjacent_players-1, player_number) for player_number in range(0, adjacent_players)] #consists of a list from 0
				denom = reduce(lambda x,y: x+y, ncr_list) #from 0 to second to last in list

				for current_player in range(1, adjacent_players+1):
					numerator = ncr_list[current_player-1] #retrieve ncr value from list
					expected_utility += ((numerator/denom)*(cell_utility/pow(current_player, 2)))

			if (expected_utility > max_utility) and (expected_utility <= self.player_list[location][player_index].capacity):
				max_utility = expected_utility
				max_utility_cell = cell
				player_amount = adjacent_players

		#this part to generate the weighted random path

		if not max_utility_cell:
			#cell weight defined by putting more weight on
			#give higher weights to those cells havent visited
			#give higher weights to those path with smallest cost
			#move dejst here
			index_path_cell = cells.index(self.rowcol_to_junction[next_node])
			average_weight = 1/len(cells)

			#generate prob distribution find the average across all cells
			prob_weight = [average_weight]*len(cells)
			prob_weight = [x-Settings.weight_random_difference if index!=index_path_cell else x+((len(cells)-1)*Settings.weight_random_difference) for index, x in enumerate(prob_weight)]
			selected_index = np.random.choice(len(cells), 1, p=prob_weight)
			max_utility_cell = cells[selected_index[0]]


		else:
			max_utility /= player_amount



		return (max_utility_cell, max_utility)




	def start_sim(self):
		#simulation start
		self.default_mode()

		#if no predefined players, randomly spawn players
		if not self.player_list:
			for i in range(Settings.car_numbers):
				row, column = randrange(self.row), randrange(self.column)
				self.add_player(row, column)


		while self.player_list:
			
			self.update()
			time.sleep(Settings.simulation_delay)
			temp_dict = {}
			for location, players in self.player_list.items():
				for i, player in enumerate(players):


					next_node = player.get_next()

					#insert logic for game theory, 
					if Settings.game_theory_algorithm:
						expect_node, reward = self.GTA_next_node(location, i, next_node)
						if expect_node: #if node return none, which means either capacity cant handle any cell reward or there are no rewards doesnt run
							#the only time this run is when the expected node is returned not none, 2 cases, either redirected based on rewards or redirected based on random weights
							next_node = self.rowcol_to_junction[expect_node]
							player = self.redirect_route(location, i, next_node, reward)

					player.node_hit.append(next_node)
					player.reward_hit.append(player.capacity)

					button_name = self.rowcol_to_junction[next_node]
					
					button_row, button_column = button_name.split('_')

					if next_node == player.destination:
						print('player has arrived from ', self.rowcol_to_junction[player.start])
						self.cap.player_list.append(player) #add player to the post processing list

					else:
						#if final destination is not reached add it to the temp dict

						if button_name in temp_dict:
							temp_dict[button_name].append(player)
						else:
							temp_dict[button_name] = [player]
					
					self.env_map.junctions[self.rowcol_to_junction[button_name]].number_players += 1
					self.env_map.junctions[self.rowcol_to_junction[location]].number_players -= 1


					self.grid_list[int(button_row)][int(button_column)].configure(bg='black')
					self.grid_list[int(button_row)][int(button_column)].configure(text=self.env_map.junctions[self.rowcol_to_junction[button_name]].number_players)



				#every time a player move away check if the edge contains more players
				player_number = self.env_map.junctions[self.rowcol_to_junction[location]].number_players
				prev_button_row, prev_button_column = location.split('_')
				if player_number == 0:
					self.grid_list[int(prev_button_row)][int(prev_button_column)].configure(bg='white')
				else:
					self.grid_list[int(prev_button_row)][int(prev_button_column)].configure(text=player_number)




			self.player_list = temp_dict
			
		print('simulation completed')
		self.reset_junction_players()

		print(self.cap.player_list)

	def clear(self):
		global mode
		if mode == 'default':
			self.player_list = {}
			self.default_mode()
		else:
			mode='default'
			self.reward_list = {}
			self.spawn_reward_mode()


	def reset_junction_players(self):
		for i in range(self.row):
			for j in range(self.column):
				string_key = str(i) + '_' + str(j)
				self.env_map.junctions[self.rowcol_to_junction[string_key]].number_players = 0




	def on_closing(self):
		self.destroy()
		traci.close()


if __name__ == "__main__":
	root = GridWin(row, column)
	root.protocol("WM_DELETE_WINDOW", root.on_closing)
	root.mainloop()