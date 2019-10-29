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
from itertools import combinations
import numpy as np



class T_test(object):

	def __init__(self, data1, data2):
		self.data1 = data1
		self.data2 = data2
		self.t_value, self.p_value = stats.ttest_ind(data1, data2, equal_var=False)
		self.get_cl()

	def __str__(self):
		return f"T:{self.t_value} P:{self.p_value} mean: {(np.mean(self.data1), np.mean(self.data2))} sd:{(np.std(self.data1), np.std(self.data2))} cl: {self.MoE} dm:{self.diff_mean} interval: {self.interval}"

	def get_cl(self):
		self.diff_mean = abs(np.mean(self.data1) - np.mean(self.data2))
		self.df = len(self.data1) + len(self.data2) - 2
		t_val = stats.t.ppf([0.975], self.df) # this is for 95% cl
		std_avg = np.sqrt(((len(self.data1) - 1)*(np.std(self.data1))**2 + (len(self.data2) - 1)*(np.std(self.data2))**2) / self.df)
		last_comp = np.sqrt(1/len(self.data1) + 1/len(self.data2))
		self.MoE = abs(t_val *std_avg * last_comp) #margin of error this is +- from diff mean to get range of 95% conf interval
		self.interval = [self.diff_mean - self.MoE, self.diff_mean + self.MoE]



class DataCapture(object): #object per simulation
	def __init__(self, map_junctions, rowcol_to_junction):
		self.player_list = [] #player node hit is inters of row column grid
		self.map_junctions = map_junctions
		self.reward_list = [] #interms of sumo junctions as key the rewards for that simulation
		self.rowcol_to_junction = rowcol_to_junction #conversion from grid to junctions
		self.reward_junction_ratio = None #ratio of total number of reward cells over total junctions
		self.setting=None


	def get_all_cells_visited(self, repeat=False):
		player_coverage_list = []
		for player in self.player_list:
			player_coverage_list.append(player.start)
			for node in player.node_hit:
				player_coverage_list.append(node)
		if repeat:
			return player_coverage_list
		return set(player_coverage_list)
		

	#{node:{hit:#, players:[]}}
	def calculate_coverage(self, repeat=False): #road utilization amount of cells visited over all cells
		return (len(self.get_all_cells_visited(repeat))/self.map_junctions)*100

	def calculate_test_coverage(self): #actually coverage amount rewarded cells visited over total reward cells
		reward_cell_visited = []
		reward_hit_number = 0

		#collected_sp_list need to contain node interms of grid

		for player in self.player_list:
			#print(f'player len node are {player.node_hit}')
			for node in player.collected_sp_list:
				if (node in self.reward_list) and (node not in reward_cell_visited):
					reward_hit_number +=1
					reward_cell_visited.append(node)
		print(f'coverage cells hit:{reward_hit_number}, total rewards cells:{len(self.reward_list)}')
		return (reward_hit_number/len(self.reward_list))*100


	def calculate_test_coverage_temp(self): #actually coverage amount rewarded cells visited over total reward cells
		reward_cell_visited = []
		reward_hit_number = 0

		#collected_sp_list need to contain node interms of grid

		for player in self.player_list:
			#print(f'player len node are {player.node_hit}')
			for node in player.collected_sp_list:
				if (node in self.reward_list):
					reward_hit_number +=1
		#print(f'coverage cells hit:{reward_hit_number}, total rewards cells:{len(self.reward_list)}')
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

	def pickle_load(self, save_path, directory=False, json_format=False):


		if directory:
			if json_format:
				files = glob.glob(os.path.join(save_path, r'*.sim'))
				for save_path in files:
					with open(save_path, 'rb') as config_dictionary_file:
						value = pickle.load(config_dictionary_file)
						player_trace = {}
						for i, player in enumerate(value.simulation_list[0].player_list):
							player_trace[i] = player.node_hit
						path_name = os.path.dirname(save_path)
						json_file = os.path.basename(save_path).split('.')[0]+'.json'
						json_file = os.path.join(path_name, json_file)
						print(f'json path is {json_file}')
						with open(json_file, 'w') as json_write:
							json.dump(player_trace, json_write)

				return
			else:
				save_path = self.find_recent_sim(save_path)

		#print('Loading from existing file... ', save_path)

		with open(save_path, 'rb') as config_dictionary_file:
			value = pickle.load(config_dictionary_file)
			return value
			
	def average_reward(self, reward_list_ret=False):
		total_reward = []
		for sim in self.simulation_list:
			sim_reward = []
			for player in sim.player_list:
				sim_reward.append(player.reward)
			total_reward.append(sum(sim_reward)/len(sim_reward))

		if reward_list_ret:
			return total_reward
		return sum(total_reward)/len(total_reward)

		

	def average(self): #average for road util
		total = 0
		for value in self.simulation_conv_list:
			total+=value
		return total/len(self.simulation_conv_list)

	def average_coverage(self):
		total = 0
		for value in self.simulation_test_coverage:
			total += value
		return total/len(self.simulation_test_coverage)


	def find_recent_sim(self, folder):
		file_list = glob.glob(os.path.join(folder, r'*.sim'))
		return max(file_list, key=os.path.getctime)


	def find_all_cov_cells(self,_iter =False):
		new_cov_test = []
		for sim in self.simulation_list:
			new_cov_test.append(sim.calculate_test_coverage_temp())

		if _iter:
			return new_cov_test
		return np.mean(new_cov_test)

	def find_all_util_cells(self):
		new_cov_test = []
		for sim in self.simulation_list:
			new_cov_test.append(sim.calculate_coverage(repeat=True))

		return np.mean(new_cov_test)

			
				









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

def autolabel(rects, ax):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{0:.2f}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


def plot_sub(folder, row_col=(2,2), capacity_change=False, box_plot=False):
	row, column = row_col[0], row_col[1]
	files = glob.glob(os.path.join(folder, r'*.sim'))
	files = [os.path.join(folder, file) for file in files]
	files.sort(key=os.path.getctime)




	divided_list = [files[i:i+4] for i, value in enumerate(files) if i%4==0]
	divided_list_four = divided_list
	divided_list = [divided_list[i:i+2] for i, x in enumerate(divided_list) if i%2==0]


	t_test_result = t_test_independent(divided_list_four) #dict of test object


	for key, value in t_test_result.items():
		if "gta" in key:
			print(key, value)


	

	if capacity_change:
		
		ru_list = []
		rc_list = []
		rw_list = []
		for i in range(row):
			for j in range(column):
				ru, rc, rw = plot_comparision(divided_list[i][j], None, capacity_change = capacity_change, box_plot=box_plot)
				ru_list.append(ru)
				rc_list.append(rc)
				rw_list.append(rw)

		for i in range(len(divided_list[-1])):
			ru_last, rc_last, rw_last = plot_comparision(divided_list[-1][i], None, capacity_change=capacity_change, box_plot = box_plot)
			ru_list.append(ru_last)
			rc_list.append(rc_last)
			rw_list.append(rw_last)

		np_ru = np.array(ru_list).T
		np_rc = np.array(rc_list).T
		np_rw = np.array(rw_list).T


		colors=['red','blue','purple','black']
	

		base_list = np_ru[0]
		for i, value in enumerate(np_ru): #change this line to nprc or npru to show road utilization or coverage
			#if i ==0:
				#continue

			#value = value/base_list

			
			plt.plot([x for x in range(10, 210, 40)], value, marker='o', markersize=5, color=colors[i], linestyle='dashed', label=files[i].split('_')[-3] if files[i].split('_')[-3] !='gta' else 'ATNE')

		#plt.yscale('log')
		plt.legend()
		plt.xticks([x for x in range(10,180,10)])
		plt.xlabel('Capacity')
		plt.ylabel('Normalized Road Utilization')


	else:
		fig, axs = plt.subplots(row, column)

		for i in range(row):
			for j in range(column):
				plot_comparision(divided_list[i][j], axs[i, j], capacity_change = capacity_change, box_plot = box_plot)

		#
		fig.tight_layout()
		#plt.xticks()
	plt.show()



def plot_comparision(files, axs, capacity_change, box_plot): #innner plot function
	#comparing base, greedy, random and gta
	#print([file.split('_')[-3] for file in files])
	#print([file.split('_')[-5] for file in files])



	if box_plot:
		ru = [MultiCapture('test').pickle_load(file, directory=False).simulation_conv_list for file in files]
		rc = [MultiCapture('test').pickle_load(file, directory=False).simulation_test_coverage for file in files]
		rw = [MultiCapture('test').pickle_load(file, directory=False).average_reward(True) for file in files]

		#Waxs.boxplot(ru)
		axs.boxplot(rc)
		axs.set_xticklabels([(file.split('_')[-3]).upper() if (file.split('_')[-3]).upper() !='GTA' else 'ATNE' for file in files])
		axs.set_yticks([x for x in range(9,22,1)])
		title = (files[0].split('_')[-5]).upper()
		axs.set_title(title)
		axs.set_xlabel('Algorithm')
		#axs.set_ylabel('Road Utilization Percentage(%)')
		axs.set_ylabel('Crowdsourcer Coverage Percentage(%)')



		return

	
	rw_mean = [MultiCapture('test').pickle_load(file, directory=False).average_reward() for file in files]

	ru_mean = [MultiCapture('test').pickle_load(file, directory=False).average() for file in files]
	#ru_mean = [MultiCapture('test').pickle_load(file, directory=False).find_all_util_cells() for file in files]
	rc_mean = [MultiCapture('test').pickle_load(file, directory=False).average_coverage() for file in files]
	#rc_mean = [MultiCapture('test').pickle_load(file, directory=False).find_all_cov_cells() for file in files]   #repeating nodes
	#print(rc_mean)

	if capacity_change: #single graph showing change in capcity vs either ru, rc or rw
		return ru_mean, rc_mean, rw_mean

	
	else:
		n_groups = len(files)
		bar_width = 0.25
		opacity = 0.8
		index = np.arange(n_groups)

		rects1 = axs.bar(index, ru_mean, bar_width, alpha=opacity, color='blue', label='Road Utilization')
		rects2 = axs.bar(index + bar_width, rc_mean, bar_width, alpha=opacity, color='green', label='Road Coverage')
		print('road utilization ', ru_mean)
		print('road coverage ', rc_mean)

		title = (files[0].split('_')[-5]).upper()

		axs.set_title(title)
		axs.set_xlabel('Algorithm')
		axs.set_ylabel('Percentage(%)')
		axs.set_yticks([x for x in range(0, 27, 2)])
		axs.set_xticks(index+(bar_width/2))
		axs.set_xticklabels([(file.split('_')[-3]).upper() if (file.split('_')[-3]).upper() !='GTA' else 'ATNE' for file in files])
		axs.legend()
		autolabel(rects1, axs)
		autolabel(rects2, axs)



def t_test_independent(files):
	

	t_test_result_dict = {}
	summary_dict = {}
	for fourfile in files:
		combs = list(combinations(fourfile, 2))
		for comb in combs:
			#sim_obj1 = MultiCapture('test').pickle_load(comb[0], directory=False).simulation_test_coverage
			#sim_obj2 = MultiCapture('test').pickle_load(comb[1], directory=False).simulation_test_coverage
			#sim_obj1 = MultiCapture('test').pickle_load(comb[0], directory=False).find_all_cov_cells(_iter=True)
			#sim_obj2 = MultiCapture('test').pickle_load(comb[1], directory=False).find_all_cov_cells(_iter=True)

			#sim_obj1 = MultiCapture('test').pickle_load(comb[0], directory=False).simulation_conv_list #road util
			#sim_obj2 = MultiCapture('test').pickle_load(comb[1], directory=False).simulation_conv_list #road util


			sim_obj1 = MultiCapture('test').pickle_load(comb[0], directory=False).average_reward(True) #utility
			sim_obj2 = MultiCapture('test').pickle_load(comb[1], directory=False).average_reward(True)

			test_obj = T_test(sim_obj1, sim_obj2)
	
			assert comb[0].split("_")[-5] == comb[1].split("_")[-5]

			key = f"{comb[0].split('_')[-3]}_{comb[1].split('_')[-3]}_{comb[0].split('_')[-5]}"
			t_test_result_dict[key] = test_obj
		
	return t_test_result_dict


	#the t value shows the difference and p value shows the significance of that difference, you want it to be <0.05 to accept the hypothesis


if __name__== "__main__":
	#obj = MultiCapture('test').pickle_load(Settings.plot_path, directory=True, json_format=False)
	#print(len(obj.simulation_list[36].get_all_cells_visited(True)), len(obj.simulation_list[36].get_all_cells_visited()))

	#print(len(obj.simulation_list[36].reward_list), obj.simulation_list[36].map_junctions) #show the ratio between reward and total cells

	#print(len(obj.simulation_list[0].reward_list), obj.simulation_list[36].map_junctions)


	plot_sub(os.path.join(Settings.sim_save_path, 'comparison'), capacity_change=True, box_plot=False)


	#generate box plot to show more details
	#ATNE
	#boxplot with normalized to baseline
	#