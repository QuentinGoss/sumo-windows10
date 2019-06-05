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
	def __init__(self, start, destination):
		self.start = start
		self.destination = destination
		self.path = None
		self.node_path = None



if __name__ == '__main__':
	play = Player((23,54))