import numpy as np
from player import Player
import heapq
from _map import Map
import traci.constants as tc
from random import choice, randrange
from settings import GraphSetting
from multiprocessing import cpu_count, Manager, Queue, Pool
import traci


class Environment(object):
	def __init__(self):
		self.map_data = Map(GraphSetting.sumo_config)
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


	def reroute(self, veh_id, current_edge, upcome_edge, destination):
		shortest_route = None
		#print(self.map_data.junctions)
		for edge in self.map_data.junctions[destination].adjacent_edges_from:
			route = traci.simulation.findRoute(upcome_edge, edge)
			if not shortest_route:
				shortest_route = route
			else:
				if route.travelTime<shortest_route.travelTime:
					shortest_route = route
		
		shortest_route = list(shortest_route.edges)
		shortest_route.insert(0, current_edge)
		try:
			traci.vehicle.setRoute(veh_id,shortest_route)
		except traci.exceptions.TraCIException as e:
			print('exception setting routes, cant u turn')
			first_seg_route = list(traci.simulation.findRoute(shortest_route[0], shortest_route[1]).edges)
			first_seg_route += shortest_route[2:]
			traci.vehicle.setRoute(veh_id,first_seg_route)


	def process_junction(self): #this function should be parallelized
		junct_data =traci.junction.getAllContextSubscriptionResults()
		for key, value in junct_data.items(): #loop through all junctions
			pre_rewards_for_junct = None #at this time step if this is calculated then just use it
			for veh, veh_value in value.items(): #loop through all vehicles in junctions
				#vehicle_info = traci.vehicle.getSubscriptionResults(veh)
				if not veh in self.junction_list[key] and self.player_list[veh].prev_junction != key:
					if not pre_rewards_for_junct:
						pre_rewards_for_junct = self.process_player(key, veh, veh_value) #if the vehicle first enter the junction process
					
					self.change_player_direction(pre_rewards_for_junct)

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

			pre_rewards_for_junct=None

	def change_player_direction(self, pre_rewards_for_junct):
		#manipulating player routes after gettign rewards and consider the player characteristics
		pass


	def process_player(self, junc_id, veh_id, veh_value):
		eu_esp_dict = {}
		for edge in self.map_data.junctions[junc_id].adjacent_junctions:
			#print(edge)
			pass
		#this function returns edge with max ultility
		#print(self.map_data.junctions[key].adjacent_junctions)
		#print(self.map_data.find_adjacent_cells(key))
		#if junc_id == 'gneJ52':
			#print(f'veh {veh_id} entered rerout junct from {veh_value[tc.VAR_ROAD_ID]}')
			#self.reroute(veh_id ,veh_value[tc.VAR_ROAD_ID], '-gneE472', GraphSetting.destination)

		#should return dict {'edgeID':{EU:'', ESP:''}}
		return eu_esp_dict






if __name__ == '__main__':
	pass