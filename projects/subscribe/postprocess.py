import numpy as np
import matplotlib.pyplot as plt
#import seaborn
import json
from operator import attrgetter
import pickle
import os, glob
from settings import Settings
class DataCapture(object): #object per simulation
	def __init__(self, map_junctions):
		self.player_list = []
		self.map_junctions = map_junctions
		

	#{node:{hit:#, players:[]}}
	def calculate_coverage(self):
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

		return (len(player_coverage_dict)/self.map_junctions)*100




class MultiCapture(object): #object for multiple simulations
	def __init__(self, title):
		self.simulation_list = []
		self.title=title
		self.simulation_conv_list = []

	def plot(self, save_path=None):
		plt.style.use('seaborn-white')
		plt.title(self.title)
		np_array = np.array(self.simulation_list)
		std, mean = np_array.std(), np_array.mean()
		plt.hist(np.array(self.simulation_list), [x for x in range(100)], density=True, histtype='bar', facecolor='b', alpha=0.5)
		plt.xlabel('Coverage (%)')
		plt.ylabel('Frequency')
		plt.text(1, 1, f'STD:{std}\nMean:{mean}', horizontalalignment='left',verticalalignment='center')
		if save_path:
			plt.savefig(save_path)
		else:
			plt.show()
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








if __name__== "__main__":
	obj = MultiCapture('test').pickle_load(Settings.sim_save_path, directory=True)
	print(obj.average())




