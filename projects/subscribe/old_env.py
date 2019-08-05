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
					
					self.change_player_direction(pre_rewards_for_junct, veh, veh_value) # pre rewards for junction is determined based on other aj junct
					

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

	def change_player_direction(self, pre_rewards_for_junct, veh_id, veh_value):
		#manipulating player routes after gettign rewards and consider the player characteristics
		choice_edge = None


		for edge, values in pre_rewards_for_junct.items():
			if not choice_edge:
				choice_edge = edge
			else:
				if (values['EU'] > pre_rewards_for_junct[choice_edge]['EU']) and (value['ESP'] <= self.player_list[veh_id].capacity):
					choice_edge = edge

		
		if pre_rewards_for_junct:
			assert choice_edge != None, 'no chosen edge error'
			self.reroute(veh_id ,veh_value[tc.VAR_ROAD_ID], choice_edge, self.player_list[veh_id].destination)

		else:
			#no need to redirct route
			#print('no route change')
			pass
		


	def find_prob_distribution(self, car_arrive_time):
		#given the time of arrival for vehicle loop through all vehicles to find probaility of the vehicle arrive at that time
		car_num = 0
		veh_result=traci.vehicle.getAllSubscriptionResults()
		#print(veh_result)





	def process_player(self, junc_id, veh_id, veh_value):
		#this should return for the junction of expected utility and expected sensing plan for the junction
		eu_esp_dict = {}
		for edge in self.map_data.junctions[junc_id].adjacent_edges_to:
			try:
				junction_to = self.map_data.edges[edge]._to
				assert self.map_data.edges[edge]._from == junc_id, 'start and end junction dont match'
				#print(edge, junction_to)
				#reward_total = self.rewards_list[junction_to] #uncomment this line
				#find the time the car can arrive at junction based on distribution
				#get the probability of all other cars arrive that junction at that time
				#calculate expected utility and sensing plan
				car_arrive_time = self.map_data.edges[edge].distance/(np.random.choice(self.map_data.edges[edge].distribution, 1)[0])
				self.find_prob_distribution(car_arrive_time)


				
			except KeyError as e:
				#edge no reward
				pass


		#this function returns edge with max ultility
		

		#should return dict {'edgeID':{EU:'', ESP:''}}
		return eu_esp_dict






if __name__ == '__main__':
	pass