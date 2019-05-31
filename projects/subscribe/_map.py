#when the car moves its always have be aware of its neighboors, need the broadcast to find the naighboor location


#this map class is handled by the server
#to update user map the server handle requests

import json
from settings import Settings
import traci
class Edge(object):
	def __init__(self, travel_time):
		print('travel time is ', travel_time)
		self.travel_time = travel_time

class Junctions(object):
	def __init__(self, coord):
		print('junction coord is ', coord)
		self.coord=coord



class Map(object):
	def __init__(self):
		'''
		load global map traci
		'''
		self.edges = {}
		self.junctions = {}
		self.populate_edges()
	@staticmethod
	def mps_to_Mph(mps):
		return ((mps * 3600)/1609.34)
	def populate_edges(self):
		for value in traci.edge.getIDList():
			self.edges[value] = Edge(traci.edge.getTraveltime(value))
	def populate_junctions(self):
		for value in traci.junction.getIDList():
			self.junctions[value] = Junctions(traci.junction.getPosition(value))








	

if __name__ =='__main__':
	my_map = Map.mps_to_Mph(2.4)
	print(my_map)
