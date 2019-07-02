
class Player(object):
	def __init__(self, veh_id, routes, passed_junction):
		self.veh_id = veh_id
		self.routes = routes
		self.index = veh_id.split('_')[1]
		self.start = routes[0]
		self.destination = routes[-1]
		self.current_edge = routes[0]
		self.capacity = 100
		self.prev_junction = passed_junction
		self.reward = 0
		
	def modify(self, routes):
		#this for when updating players
		self.routes = routes
		self.current_edge = routes[0]
		
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
		self.expected_reward = 0
		self.reward=0

	def get_next(self):
		#print(self.node_path, self.node_index)
		value= self.node_path[self.node_index]
		self.node_index+=1
		return value


	def __repr__(self):
		#return repr((self.start, self.destination, self.node_hit, self.reward_hit))
		return repr((self.start, self.destination))

