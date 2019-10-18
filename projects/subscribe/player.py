
class Player(object):
	def __init__(self, veh_id, routes, passed_junction, dest_junc, target_poi=None):
		self.veh_id = veh_id
		self.routes = routes
		self.index = veh_id.split('_')[1]
		self.start = routes[0]
		self.dest_junc = dest_junc
		self.destination = routes[-1]
		self.current_edge = routes[0]
		self.capacity = 100
		self.prev_junction = passed_junction
		self.prev_poi = None
		self.prev_poi_junct = None
		self.reward = 0
		self.target_poi = target_poi #the poi that the veicle is currently going towards
		self.current_poi_distribution = {} #distribution buckets to every poi
		self.temp_edges = {} #edges to every poi
		self.participation = True
		
	def modify(self, routes):
		#this for when updating players
		self.routes = routes
		self.current_edge = routes[0]

		
class GridPlayer(object):
	def __init__(self, start, destination):
		self.node_hit = [] #for post processing keep track of all the nodes its been through
		self.collected_sp_list = []  #for calculated real coverage and not ru
		self.reward_hit = [] # for post processing keep track of the capacity at each node
		self.node_index = 0
		self.start = start
		self.destination = destination
		self.path = None
		self.node_path = None 
		self.capacity = 100
		self.reward=0
		self.past_recent_nodes = [] #short term memory, in terms of grid junction
		self.participation = True

	def get_next(self):
		#print(self.node_path, self.node_index)
		value= self.node_path[self.node_index]
		self.node_index+=1
		return value


	def __repr__(self):
		#return repr((self.start, self.destination, self.node_hit, self.reward_hit))
		return repr((self.start, self.destination))

