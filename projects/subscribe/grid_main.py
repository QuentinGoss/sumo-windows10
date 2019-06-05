import tkinter as tk
import traci
from _map import Map
from player import GridPlayer
from random import randrange
from settings import Settings
import time


row = 11
column = 11





class GridWin(tk.Tk):
	def __init__(self, row, column):
		super(GridWin, self).__init__()
		traci.start(["sumo", "-c", Settings.sumo_config])

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
		self.rewards = {} #stores location as key, reward value as value



		self.spawn_grid()
		self.control_buttons()

	def control_buttons(self):
		start_sim_button = tk.Button(self.control_frame, text='start simulation', command=self.start_sim)
		start_sim_button.pack(expand=True, fill='both')

		select_cars = tk.Button(self.control_frame, text='spawn cars')
		select_cars.pack(expand=True, fill='both')

		select_rewards = tk.Button(self.control_frame, text='choose rewards')
		select_rewards.pack(expand=True, fill='both')

	def spawn_grid(self):
		for i in range(row):
			temp_list = []
			for j in range(column):
				b= tk.Button(self.grid_frame)
				b.grid(row=i, column=j, sticky=tk.N+tk.S+tk.W+tk.E, columnspan=1)
				self.grid_frame.grid_columnconfigure(j, weight=2)
				self.grid_frame.grid_rowconfigure(i, weight=2)
				temp_list.append(b)
			self.grid_list.append(temp_list)

	def start_sim(self):
		if not self.player_list:
			for i in range(5):
				row, column = randrange(self.row), randrange(self.column)
				string_key = str(row) + '_' + str(column)
				#print('starting in ', self.rowcol_to_junction[string_key])
				player_instance = GridPlayer(self.rowcol_to_junction[string_key], self.rowcol_to_junction['0_0'])

				if player_instance.start != player_instance.destination:
					player_instance.path = self.env_map.find_best_route(player_instance.start, player_instance.destination)
					player_instance.node_path = [self.env_map.edges[x]._to for x in player_instance.path.edges]

					#print(player_instance.node_path)


					if string_key in self.player_list:
						self.player_list[string_key].append(player_instance)
					else:
						self.player_list[string_key] = [player_instance]
						self.grid_list[row][column].configure(bg='black')

					self.env_map.junctions[self.rowcol_to_junction[string_key]].number_players += 1





		
		while self.player_list:
			
			self.update()
			time.sleep(1)
			temp_dict = {}
			for location, players in self.player_list.items():
				for player in players:
					try:
						button_name = self.rowcol_to_junction[player.get_next()]
					except AssertionError:
						print('player has arrived from ', self.rowcol_to_junction[player.start])
						continue
					button_row, button_column = button_name.split('_')
					

					#this should be in a function or something
					if button_name in temp_dict:
						temp_dict[button_name].append(player)
					else:
						temp_dict[button_name] = [player]
						self.grid_list[int(button_row)][int(button_column)].configure(bg='black')

					self.env_map.junctions[self.rowcol_to_junction[button_name]].number_players += 1



					#every time a player move away check if the edge contains more players
					player_number = self.env_map.junctions[self.rowcol_to_junction[location]].get_player_number()
					if player_number == 0:
						prev_button_row, prev_button_column = location.split('_')
						self.grid_list[int(prev_button_row)][int(prev_button_column)].configure(bg='white')


				self.player_list = temp_dict
			
		print('simulation completed')




	def on_closing(self):
		self.destroy()
		traci.close()


if __name__ == "__main__":
	root = GridWin(row, column)
	root.protocol("WM_DELETE_WINDOW", root.on_closing)
	root.mainloop()