import numpy as np
import matplotlib.pyplot as plt
#import seaborn
import json
from operator import attrgetter
import pickle
import os, glob
from settings import Settings
import pandas as pd
from scipy import stats



class DataCapture(object): #object per simulation
	def __init__(self, map_junctions, rowcol_to_junction):
		self.player_list = [] #player node hit is inters of row column grid
		self.map_junctions = map_junctions
		self.reward_list = [] #interms of sumo junctions as key
		self.rowcol_to_junction = rowcol_to_junction
		self.reward_junction_ratio = None #ratio of total number of reward cells over total junctions
		self.setting=None
		

	#{node:{hit:#, players:[]}}
	def calculate_coverage(self): #road utilization amount of cells visited over all cells
		player_coverage_dict = {}
		for player in self.player_list:
			player_coverage_dict[player.start] = {'hit':1, 'player_list':[player]}
			for node in player.node_hit:
				if node in player_coverage_dict:
					player_coverage_dict[node]['hit'] +=1
					if not player in player_coverage_dict[node]['player_list']:
						player_coverage_dict[node]['player_list'].append(player)
				else:
					player_coverage_dict[node] = {'hit':1, 'player_list':[player]}
		print(f'road utilization cells hit:{len(player_coverage_dict)}, total sumo cells:{self.map_junctions}')
		return (len(player_coverage_dict)/self.map_junctions)*100

	def calculate_test_coverage(self): #actually coverage amount rewarded cells visited over total reward cells
		reward_cell_visited = []
		reward_hit_number = 0
		#print(self.reward_list)
		#print(f'len player are {len(self.player_list)}, reward list len is {len(self.reward_list)}')
		for player in self.player_list:
			#print(f'player len node are {player.node_hit}')
			for node in player.collected_sp_list:
				if (self.rowcol_to_junction[node] in self.reward_list) and (node not in reward_cell_visited):
					reward_hit_number +=1
					reward_cell_visited.append(node)
		print(f'coverage cells hit:{reward_hit_number}, total rewards cells:{len(self.reward_list)}')
		return (reward_hit_number/len(self.reward_list))*100



class MultiCapture(object): #object for multiple simulations
	def __init__(self, title):
		self.simulation_list = []
		self.title=title
		self.simulation_conv_list = []
		self.simulation_test_coverage = []



	def pickle_save(self, save_path):
		with open(save_path, 'wb') as config_dictionary_file:
			pickle.dump(self, config_dictionary_file)
		print('simulation saved success...')

	def pickle_load(self, save_path, directory=False):

		if directory:
			save_path = self.find_recent_sim(save_path)

		print('Loading from existing file... ', save_path)

		with open(save_path, 'rb') as config_dictionary_file:
			return pickle.load(config_dictionary_file)
			

		

	def average(self):
		total = 0
		for value in self.simulation_conv_list:
			total+=value

		return total/len(self.simulation_conv_list)

	def find_recent_sim(self, folder):
		file_list = glob.glob(os.path.join(folder, r'*.sim'))
		return max(file_list, key=os.path.getctime)





def plot_graph_folder(folder, x_interval,x_label,y_label): #plot the graph based on the mean of the simulation
	file_list = glob.glob(os.path.join(folder, r'*.sim'))
	file_list.sort(key=os.path.getctime)

	y_interval = [MultiCapture('test').pickle_load(x, directory=False).average() for x in file_list]

	plt.plot(x_interval, y_interval, marker='o', markersize=5, color='black', linestyle='dashed')
	#plt.plot(np.unique(x_interval), np.poly1d(np.polyfit(x_interval, y_interval, 1))(np.unique(x_interval)), color='black')
	#for xy in zip(x_interval, y_interval):                         
   		#plt.annotate(f'{xy[1]:.2f}%', xy=xy, textcoords='data')

	plt.xlabel(x_label)
	plt.ylabel(y_label)
	#plt.grid()
	plt.show()


def plot_graph_multiple(folder, x_label, y_label, catogories): # x-axis number of simulation steps, y is the coverage, and multiple lines representing each capacity or budget value
	file_list = glob.glob(os.path.join(folder, r'*.sim'))
	file_list.sort(key=os.path.getctime)
	y_interval = [[j for j in MultiCapture('test').pickle_load(x, directory=False).simulation_conv_list] for x in file_list]
	x_interval = [x for x in range(1, len(y_interval[0])+1)]

	colors=['red','blue','yellow','purple','black']

	for i, simulation in enumerate(y_interval):
		plt.plot(x_interval, simulation, marker='o', markersize=4, color=colors[i], linestyle='', label=catogories[i])
		plt.plot(np.unique(x_interval), np.poly1d(np.polyfit(x_interval, simulation, 1))(np.unique(x_interval)), color=colors[i])
	plt.legend(loc='best')
	plt.grid()
	plt.show()





if __name__== "__main__":
	obj = MultiCapture('test').pickle_load(Settings.plot_path, directory=True)
	print(obj.average())

	#plot_graph_folder(os.path.join(Settings.sim_save_path, 'change capacity 40'), [x for x in range(10, 210, 40)], x_label='Capacity Mean Value', y_label='Coverage (%)')
	#plot_graph_multiple(os.path.join(Settings.sim_save_path, 'change capacity'), 'capacity','coverage', [x for x in range(10,60,10)])

