from settings import Settings
import json
class Player(object):
	def __init__(self, index, coord, destination=None, speed=None, edge=None):
		self.index_value = index
		self.coord = coord
		self.destination = destination
		self.speed = speed
		self.edge = edge
		

if __name__ == '__main__':
	play = Player((23,54))