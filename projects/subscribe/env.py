import numpy as np
from player import Player
import heapq
from _map import Map
import traci.constants as tc
from random import choice, randrange
from settings import GraphSetting
from multiprocessing import cpu_count, Manager, Queue, Pool
import traci
from operator import itemgetter
import itertools
from util import *


class Environment(object):
	def __init__(self):
		self.map_data = Map(GraphSetting.sumo_config)
		self.player_list = {}
		self.rewards_list = {}
		
		self.index_counter = 0

		self.poi_to_junct = {}

		self.poi_list = {}
		self.player_location_array = None #array storing location

	def calculate_next_poi(self, player, add=False):#add to show that its initializing
		#this is called when player is added and is called every time a play arrived at a poi
		#loops through every player and every poi to find the player prob for every poi



		max_eu = 0
		max_eu_location=None

		len_player = len(self.player_list)

		for location, value in self.rewards_list.items():
			e_u = 0
			e_sp = 0

			assert len_player >0, 'something is wrong no player in system'

			if len_player <=1:
				e_u = value
				e_sp = self.map_data.junctions[location].cost
			else:
				#if more than one player in the sytem

				if add:
					player_data = self.player_list
				else:
					player_data = traci.vehicle.getAllSubscriptionResults()

				for veh_id, veh_value in player_data.items():
					temp_eu, temp_esp = self.calculate_utility(veh_id, location, value, add=add)
					e_u += temp_eu
					e_sp += temp_esp
			print(e_sp)

			if (e_u > max_eu) and (e_sp <= player.capacity) and (location!=player.target_poi):
				max_eu = e_u
				max_eu_location = location




		return max_eu_location



			
			
	def generate_bucket(self, veh_id=None):
		if veh_id: #finding dict for only 1 vehicle
			for key, value in self.rewards_list.items():
				route_edges = self.find_route_reroute(self.player_list[veh_id].current_edge, key).edges
				self.player_list[veh_id].temp_edges[key]=route_edges
				list_dist = np.array([self.map_data.edges[e].distribution_time for e in route_edges if not ':' in e])
				route_array = np.sum(list_dist, axis=0)
				result = np.histogram(route_array, bins=np.linspace(np.min(route_array), np.max(route_array), num=6))
				result = (result[0]/np.sum(result[0]), result[1])
				self.player_list[veh_id].current_poi_distribution[key] = result
		else:
			for veh_id, veh_value in traci.vehicle.getAllSubscriptionResults().items():
				for key, value in self.rewards_list.items():
					route_edges = self.find_route_reroute(veh_value[tc.VAR_ROAD_ID], key).edges
					self.player_list[veh_id].temp_edges[key]=route_edges
					list_dist = np.array([self.map_data.edges[e].distribution_time for e in route_edges if not ':' in e])
					route_array = np.sum(list_dist, axis=0)
					result = np.histogram(route_array, bins=np.linspace(np.min(route_array), np.max(route_array), num=6))
					result = (result[0]/np.sum(result[0]), result[1])
					self.player_list[veh_id].current_poi_distribution[key] = result


	def generate_mesh_grid(self, player_list, current_player, player_num):
		'''
		mesh_array = [[current_player]]
		
		player_list.remove(current_player)


		for i in range(player_num-1):
			mesh_array.append(player_list)


		#print(f'mesh array for player {player_num} is {mesh_array}, current player is {current_player}')
		mesh_grid = np.array(np.meshgrid(*mesh_array)).T.reshape(-1,player_num)

		#mesh_grid = mesh_grid[np.where(np.array_equal(np.unique(mesh_grid), mesh_grid))]
		return mesh_grid
		'''
		#need to return [[veh1, veh2]]
		player_list.remove(current_player)
		mesh_grid = list(itertools.combinations(player_list, player_num-1))
		#print(mesh_grid)

		return mesh_grid

	def compute_sensing_plan(self, player_amount, reward, cost):
		print('player amount is ', player_amount)
		sensing_plan = ((player_amount-1)*reward)/((player_amount**2)*cost)

		#print('sensning plan value is ', sensing_plan)
		return sensing_plan


			
	def calculate_utility(self, veh_id, location, reward, add=False): #based on given vehicle id and target location do algo
		if add:
			player_data = self.player_list
		else:
			player_data = traci.vehicle.getAllSubscriptionResults()

		player_data_keys = list(player_data.keys())

		e_u_list = [] #contains the utility of up to n players
		e_sp_list = []

		#for each player, for each bucket in the
		for index, time in enumerate(self.player_list[veh_id].current_poi_distribution[location][1]):
			#print('current car bucket', bucket)
			expected_utility_final = 0
			expected_sensing_final = 0

			#print('self prob is ', self_time_prob)

			for i in range(1, len(player_data_keys)+1):
				reward_value = reward/pow(i, 2)
				prob = 1
				if i == 1:
					for veh_id_new, veh_value in player_data.items():
						if veh_id == veh_id_new:
							prob *= self.find_prob_given_time(time, veh_id, location)
						else:
							prob *= (1 - self.find_prob_given_time(time, veh_id_new, location))

					

				else:
					self_time_prob = self.player_list[veh_id].current_poi_distribution[location][0][index]


					#print('before mesh grid ', player_data_keys)
					mesh_grid = self.generate_mesh_grid(player_data_keys, veh_id, i)
					player_data_keys = list(player_data.keys())

					for comb in mesh_grid: #loop through each possibility
						for veh_id_new, veh_value in player_data.items():
							if veh_id_new in comb:
								temp_prob = self.find_prob_given_time(time, veh_id_new, location)
								if temp_prob != 0: #this part
									prob *= temp_prob
							else:
								temp_prob = (1 - self.find_prob_given_time(time, veh_id_new, location))
								if temp_prob != 0:
									prob *= temp_prob
						
						prob*=self_time_prob

				expected_utility_final += (prob*reward_value)
				expected_sensing_final += (prob*self.compute_sensing_plan(i, reward_value, self.map_data.junctions[location].cost))

			e_u_list.append(expected_utility_final)
			e_sp_list.append(expected_sensing_final)

			return sum(e_u_list), sum(e_sp_list)


	def find_prob_given_time(self, time, veh_id_new, location):

		buckets = self.player_list[veh_id_new].current_poi_distribution[location][1]

		try:
			upper = np.min(np.where(buckets>time))
			lower = np.max(np.where(buckets<time))
		except ValueError:
			lower = None

		if not lower:
			return 0
		else:
			return self.player_list[veh_id_new].current_poi_distribution[location][0][lower]
			


	def add_player(self, veh_id, routes, dest_junct):
		if not veh_id in self.player_list:
			assert self.index_counter == int(veh_id.split('_')[1]), 'player id doesnt match counter'
			self.player_list[veh_id] = Player(veh_id, routes, self.map_data.edges[routes[0]]._from, dest_junct)
			self.player_list[veh_id].capacity = get_truncated_normal(GraphSetting.player_reward_random[0], GraphSetting.player_reward_random[1], 0, GraphSetting.player_reward_random[0]*2).rvs(1)[0]
			self.generate_bucket(veh_id=veh_id)
			self.player_list[veh_id].target_poi = self.calculate_next_poi(self.player_list[veh_id], add=True)
			self.reroute(veh_id, None, self.player_list[veh_id].start,self.player_list[veh_id].target_poi)
			self.index_counter+=1

		else:
			self.player_list[veh_id].modify(routes)


	def find_route_reroute(self, upcome_edge, destination):
		shortest_route = None
		#print(self.map_data.junctions)
		for edge in self.map_data.junctions[destination].adjacent_edges_from:
			route = traci.simulation.findRoute(upcome_edge, edge)
			if not shortest_route:
				shortest_route = route
			else:
				if route.travelTime<shortest_route.travelTime:
					shortest_route = route

		return shortest_route



	def reroute(self, veh_id, current_edge, upcome_edge, destination): 
		print(f'vehicle {veh_id} change direction going towards {destination}')
		shortest_route = self.find_route_reroute(upcome_edge, destination)
		
		shortest_route = list(shortest_route.edges)
		if current_edge:
			shortest_route.insert(0, current_edge)
		try:
			traci.vehicle.setRoute(veh_id,shortest_route)
		except traci.exceptions.TraCIException as e:
			print('exception setting routes, cant u turn')
			first_seg_route = list(traci.simulation.findRoute(shortest_route[0], shortest_route[1]).edges)
			first_seg_route += shortest_route[2:]
			traci.vehicle.setRoute(veh_id,first_seg_route)

	def update_capacity(self, veh, esp):
		try:
			self.player_list[veh].capacity -= esp
		except KeyError:
			print(veh_value, 'Error')

	def update_veh_collection_status(self, veh_value, poi_key):
		#iterate through all the vehicles
		for i in range(len(veh_value), 0, -1):
			esp = self.compute_sensing_plan(i, self.rewards_list[self.poi_to_junct[poi_key]], self.map_data.junctions[self.poi_to_junct[poi_key]].cost)
			counter = 0 #this to count how many fits the capacity
			for new_key, new_value in veh_value.items():
				if esp<=self.player_list[new_key].capacity:
					counter+=1
					self.player_list[new_key].participation = True
				else:
					self.player_list[new_key].participation = False
			if counter == i:
				if i==1:
					esp = self.map_data.junctions[self.poi_to_junct[poi_key]].cost
				return esp, i






	def process_poi(self):
		poi_data = traci.poi.getAllContextSubscriptionResults()
		if poi_data:
			for key, value in poi_data.items(): #loop through all poi list

				self.generate_bucket() #update players prob dist buckets for every reward
				esp, number_players = self.update_veh_collection_status(value, key) #update all the vehicles at the junction for if they are participating or not
				#print(f'esp is {esp}, {number_players}')
				for veh, veh_value in value.items(): #loop through all vehicles in junctions
					if not veh in self.poi_list[key] and self.player_list[veh].prev_poi != key: #this if statement for when vehicle first enter junction
						#update capacity and reward first

						#print('vehicle approaching poi', veh, key)
						if self.player_list[veh].participation:
							self.update_capacity(veh, esp)

						next_poi = self.calculate_next_poi(self.player_list[veh])

						if not next_poi:
							#this is the weighted random jumps

							print('vehicle reached max capacity, going towards destination')
							next_poi = self.player_list[veh].dest_junc

						self.player_list[veh].target_poi = next_poi

						self.reroute(veh, None, veh_value[tc.VAR_ROAD_ID], next_poi)



						#print(f'vehicle {veh} arrived at poi {key}, next poi is {next_poi}, destination is {self.player_list[veh].dest_junc}')

						self.poi_list[key][veh] = veh_value

					elif veh in self.poi_list[key] and self.player_list[veh].prev_poi != key:
						#check if it should delete vehicle
						try:
							if self.map_data.edges[veh_value[tc.VAR_ROAD_ID]]._to != key:
								#print('vehicle left junction')
								self.player_list[veh].prev_poi = key
								del self.poi_list[key][veh]
						except KeyError:
							#print('reached junction')
							continue




if __name__ == '__main__':
	pass