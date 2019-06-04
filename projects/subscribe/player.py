from settings import Settings
import json
import traci
class Player(object):
	def __init__(self, index, coord, destination=None, speed=None, edge=None):
		self.index_value = index
		self.coord = coord
		self.destination = destination
		self.speed = speed
		self.edge = edge
		
class GridPlayer(object):
	def __init__(self, index, destination):
		self.index = index
		self.destination = destination
		self.path = []


if __name__ == '__main__':
	play = Player((23,54))