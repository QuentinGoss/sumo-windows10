#when the car moves its always have be aware of its neighboors, need the broadcast to find the naighboor location


#this map class is handled by the server
#to update user map the server handle requests

import json
from settings import Settings
class Map(object):
	def __init__(self):
		'''
		load global map from json, 
		'''
		with open(Settings.map_path, 'r') as f:
			self.global_map = json.load(f)
		self.processed_map = self.map_process()

	def get_local_map(self, coords, radius):
		'''
		takes in coords of the player and setting raidus, return local map for player

		'''
		return {'test':'mapdata'}
	
	def map_process(self):
		'''
		take all the nodes
		'''
		map_temp = {}
		for key, value in self.global_map.items():
			print(key)


	def broad_cast(self, message):
		pass

if __name__ =='__main__':
	my_map = Map()
