import numpy as np
from player import Player
import heapq
from _map import Map
import traci.constants as tc
from random import choice, randrange
from settings import Settings
from multiprocessing import cpu_count, Manager, Queue, Pool
import traci


class Environment(object):
	def __init__(self):
		self.map_data = Map(Settings.sumo_config)
		self.player_list = {}
		self.junction_list = {k:dict() for k in self.map_data.junctions.keys()}
		self.rewards_list = {}
		
		self.index_counter = 0


		self.player_location_array = None #array storing location

	def add_player(self, veh_id, routes):
		if not veh_id in self.player_list:
			assert self.index_counter == int(veh_id.split('_')[1]), 'player id doesnt match counter'
			self.player_list[veh_id] = Player(veh_id, routes, self.map_data.edges[routes[0]]._from)
			self.index_counter+=1
		else:
			self.player_list[veh_id].modify(routes)

	def process_junction(self): #this function should be parallelized
		junct_data =traci.junction.getAllContextSubscriptionResults()
		for key, value in junct_data.items():
			for veh, veh_value in value.items():
				#vehicle_info = traci.vehicle.getSubscriptionResults(veh)
				if not veh in self.junction_list[key] and self.player_list[veh].prev_junction != key:
					print(f'vehicle {veh} just entered in junction {key}')
					self.process_player(veh, veh_value, key)
					self.junction_list[key][veh] = veh_value

				elif veh in self.junction_list[key] and self.player_list[veh].prev_junction != key:
					#check if it should delete vehicle
					try:
						if self.map_data.edges[veh_value[tc.VAR_ROAD_ID]]._to != key:
							#print('vehicle left junction')
							self.player_list[veh].prev_junction = key
							del self.junction_list[key][veh]
					except KeyError:
						#print('reached junction')
						continue

	def process_player(self, veh_id, veh_value, key):
		print(self.map_data.junctions[key].adjacent_junctions)
		print(self.map_data.find_adjacent_cells(key))





if __name__ == '__main__':
	pass