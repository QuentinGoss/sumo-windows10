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


row = 11
column = 11

mode='default' #default, vehicle, reward



class GridWin(tk.Tk):
	def __init__(self, row, column):
		super(GridWin, self).__init__()
		traci.start(["sumo", "-c", Settings.sumo_config])

		w=self.winfo_screenwidth()
		h=self.winfo_screenheight()
		size = str(int(w/2))+'x'+str(int(h/2))
		print(size)
		self.geometry(size)

		self.row = row
		self.column = column
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
		return numer / denom


	
	def spawn_reward_mode(self):
		global mode
		if mode == 'default':
			mode='reward'


			for i in range(row):
				for j in range(column):
					string_key = str(i) + '_' + str(j)
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


		select_rewards = tk.Button(self.control_frame, text='choose rewards', command = self.spawn_reward_mode)
		select_rewards.pack(expand=True, fill='both')

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
			player_num +=len(self.player_list[value])
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

		#if max_num and (string_key in self.player_list):
			#if len(self.player_list[string_key]) == max_num:
				#the current cell reach the max number of vehicles
			#	return


		player_instance = GridPlayer(self.rowcol_to_junction[string_key], self.rowcol_to_junction['0_0'])
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




	def start_sim(self):
		#global mode
		#if mode != 'default':
		self.default_mode()

		if not self.player_list:
			for i in range(Settings.car_numbers):
				row, column = randrange(self.row), randrange(self.column)
				self.add_player(row, column)


		while self.player_list:
			
			self.update()
			time.sleep(Settings.simulation_delay)
			temp_dict = {}
			for location, players in self.player_list.items():
				for player in players:


					next_node = player.get_next()
					button_name = self.rowcol_to_junction[next_node]
					button_row, button_column = button_name.split('_')

					if next_node == player.node_path[-1]:
						print('player has arrived from ', self.rowcol_to_junction[player.start])
						

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
		self.env_map.junctions[self.rowcol_to_junction['0_0']].number_players = 0 #after finish refresh the destination node to 0





	def on_closing(self):
		self.destroy()
		traci.close()


if __name__ == "__main__":
	root = GridWin(row, column)
	root.protocol("WM_DELETE_WINDOW", root.on_closing)
	root.mainloop()