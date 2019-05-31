import numpy as np
from player import Player
import heapq
from _map import Map
import traci.constants as tc

class Environment(object):
	def __init__(self):
		self.player_data = {}
		self.map_data = Map()
		self.index_counter = 0

	def distribute_rewards(self):
		pass

	def populate_players(self, data):
		for key, value in data.items():
			#print(value)
			if key in self.player_data:

				if value[tc.VAR_ROUTE_INDEX] == (len(value[tc.VAR_EDGES]) - 1):
					#print('Vehicle {} has arrived at {} current road is {}'.format(key, value[tc.VAR_EDGES][-1], value[tc.VAR_ROAD_ID]))
					del self.player_data[key]
				else:
					self.modify_object(key, value)
			else:
				self.player_data[key] = Player(self.index_counter, value[tc.VAR_POSITION], value[tc.VAR_EDGES][-1], value[tc.VAR_SPEED])
				self.index_counter+=1


	def modify_object(self, key, value):
		self.player_data[key].coord = value[tc.VAR_POSITION]
		self.player_data[key].speed = value[tc.VAR_SPEED]
		self.player_data[key].destination = value[tc.VAR_EDGES][-1]

		


			





if __name__ == '__main__':
	pass