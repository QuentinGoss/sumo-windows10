import tkinter as tk


class GridWin(tk.Tk):
	def __init__(self, row, column):
		super(GridWin, self).__init__()


		self.protocol("WM_DELETE_WINDOW", self.on_closing)
		w=self.winfo_screenwidth()
		h=self.winfo_screenheight()
		size = str(int(w/2))+'x'+str(int(h/2))
		#print(size)
		self.geometry(size)

		self.row = row
		self.column = column

		self.import_frame = tk.Frame(self, bg='green')
		#self.import_frame.pack(expand=True, fill='both')

		self.grid_frame = tk.Frame(self, height=500, width=500, bg='red')
		self.grid_frame.pack(expand=True, fill='both')

		self.control_frame = tk.Frame(self)
		self.control_frame.pack(expand=True, fill='both')


		self.grid_list = []

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

				self.grid_list[i][j].configure(command = lambda i=i, j=j: self.add_player(i, j))
				self.grid_list[i][j].bind('<Button-3>', lambda event, a=i, b=j, color=self.default_button_color: self.remove_player(a, b, color))
				self.grid_list[i][j].bind('<Button-2>', lambda event, a=i, b=j: self.normal_distribute_players(a,b))
				self.grid_list[i][j].configure(fg='white')

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




	
