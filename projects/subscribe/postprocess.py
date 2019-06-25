import numpy as np
import matplotlib.pyplot as plt
#import seaborn
import json
from operator import attrgetter
class DataCapture(object): #object per simulation
	def __init__(self, row, column):
		self.player_list = []
		self.row = row
		self.column = column
		

	#{node:{hit:#, players:[]}}
	def calculate_coverage(self):
		total_cells = (self.row * self.column)
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
		return (len(player_coverage_dict)/total_cells)*100
		#print(f'Total coverage {len(player_coverage_dict)} out of {total_cells} cells, {(len(player_coverage_dict)/total_cells)*100}%')
		#print(f'Total Number player arrived {len(self.player_list)}')
		#print(player_coverage_dict)




class MultiCapture(object): #object for multiple simulations
	def __init__(self, title):
		self.simulation_list = []
		self.title=title

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