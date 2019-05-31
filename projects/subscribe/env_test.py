import matplotlib.pyplot as plt
import nashpy
import numpy as np
from player import Player
from random import randrange
import heapq
import _map
#create a environment to randomly set players locations



class Environment(object):
	def __init__(self, num_players):
		self.num_players = num_players
		self.player_list = {} #dict to store players index as key and object as value
		#self.coord_np = self.update_coords()
	def update_coords(self):
		
		if not self.player_list:
			numpy_list = []
			for i in range(self.num_players):
				p = Player((randrange(100), randrange(100)), i)
				self.player_list[i] = p #the index is the player id
				numpy_list.append(list(p.coords))
			return np.array(numpy_list)
		else: #the player_list already filled
			for key, value in self.player_list.items(): #modify each value in numpy array according to dict
				self.coord_np[value.index_value] = list(value.coords)
			return self.coord_np

	def add_player(self, coords=None):
		'''
		adding player to dict and adding its coords to np array
		'''
		p = Player((randrange(100), randrange(100)), index=self.coord_np.shape[0])
		self.coord_np=np.append(self.coord_np, [list(p.coords)], axis=0)
		self.player_list[p.index_value] = p
		
		
	def find_all_player(self, coords, radius, amount=None):
		'''
		find all players around the coords
		radius specify the distance from coords
		amount is the number of players returned. 3 means the closest 3 to the coord
		'''
		print(self.coord_np)
		distances = np.linalg.norm(list(coords) - self.coord_np, axis=1)

		indexes = np.where(distances <= radius) #axis needs to be one apply to column of every row

		if amount:
			dtype = [('index', int),('distance', float)]
			array_sort = np.sort(np.array(list(zip(indexes[0], distances[indexes])), dtype=dtype), order='distance')
			print(array_sort[:amount])
			





if __name__ == '__main__':
	env = Environment(3)
	env.find_all_player((50,50), 40)
	print(env.player_list)
	env.add_player()
	print()
	print(env.player_list)