from settings import Settings
import json
class Player(object):
	def __init__(self, index, coord, destination=None, speed=None):
		self.index_value = index
		self.coord = coord
		self.destination = None
		self.speed = 0
		

if __name__ == '__main__':
	play = Player((23,54))