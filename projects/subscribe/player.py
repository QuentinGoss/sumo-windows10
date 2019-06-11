
class Player(object):
	def __init__(self, index, coord, destination=None, speed=None, edge=None):
		self.index_value = index
		self.coord = coord
		self.destination = destination
		self.speed = speed
		self.edge = edge
		
class GridPlayer(object):
	def __init__(self, start, destination):
		self.node_hit = [] #for post processing keep track of all the nodes its been through
		self.reward_hit = [] # for post processing keep track of the capacity at each node
		self.node_index = 0
		self.start = start
		self.destination = destination
		self.path = None
		self.node_path = None 
		self.capacity = 100

	def get_next(self):
		value= self.node_path[self.node_index]
		self.node_index+=1
		return value


	def __repr__(self):
		return repr((self.start, self.destination, self.node_hit, self.reward_hit))

