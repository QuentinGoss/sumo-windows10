import numpy as np
from player import Player
import heapq
from _map import Map
import traci.constants as tc
from random import choice, randrange
import traci

class Environment(object):
	def __init__(self):
		self.player_data = {}
		self.map_data = Map()
		self.rewards = {}
		self.index_counter = 0

	def distribute_rewards(self):
		pass

	def initial(self):
		self.initial_route_random(1)


	def initial_route_random(self, amount):
		list_edges = [x for x in traci.edge.getIDList() if not ':' in x]
		#print(list_edges)
		for i in range(amount):
			traci.route.add('route'+str(i), [choice(list_edges) for _ in range(2)])
			traci.vehicle.add('veh'+str(i), 'route'+str(i), typeID='chevy_s10',departLane='random')
			#route = traci.simulation.findRoute(traci.route.getEdges('route'+str(i))[0], traci.route.getEdges('route'+str(i))[1])
			#print(route.edges)






	def populate_players(self, data):
		arrived_list = traci.simulation.getArrivedIDList()
		for key, value in data.items():

			if key in self.player_data:
				#traci.vehicle.setColor(key,(255, 255, 255))
				if key in arrived_list:
					del self.player_data[key]
				else:
					self.modify_object(key, value)
			else:

				self.player_data[key] = Player(self.index_counter, value[tc.VAR_POSITION], value[tc.VAR_EDGES][-1], value[tc.VAR_SPEED], value[tc.VAR_ROAD_ID])
				self.index_counter+=1
				#traci.vehicle.setColor(key,(randrange(255), randrange(255), randrange(255)))


	def modify_object(self, key, value):
		self.player_data[key].coord = value[tc.VAR_POSITION]
		self.player_data[key].speed = value[tc.VAR_SPEED]
		self.player_data[key].destination = value[tc.VAR_EDGES][-1]


	
	def generate_elements(self):
		s_elements = "\t" + config.s_vtype + "\n"
		return s_elements

	@staticmethod
	def generate_routefile(self): 
		with open(config.s_route_file,"w") as routes:
			print("<routes>", file=routes)
			s_elements = self.generate_elements()
			print(s_elements, file=routes)
			print("</routes>", file=routes)


			





if __name__ == '__main__':
	pass