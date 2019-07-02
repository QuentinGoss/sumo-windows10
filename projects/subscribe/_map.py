#when the car moves its always have be aware of its neighboors, need the broadcast to find the naighboor location


#this map class is handled by the server
#to update user map the server handle requests
from util import *
from xml.dom import minidom
from settings import Settings
import traci
from operator import attrgetter
from concurrent.futures import ProcessPoolExecutor as pool
from multiprocessing import cpu_count
import os
import math

class Edge(object):
	def __init__(self, _from, _to, speed, distance):
		self._from = _from
		self._to = _to
		self.speed = speed
		self.distance = distance
		self.std = 1
		self.distribution = self.generate_speed_distribution()

	def generate_speed_distribution(self, amount=10000, file=None):
		if not file:
			#if no pparse generate with mean as speed limit, std=1 and max speed is 200
			return get_truncated_normal(self.speed,upp=200).rvs(amount)

		

class Junctions(object):
	def __init__(self, coord, junction_id):
		#each junction would contain a utility matrix showing
		self.junction_id = junction_id
		self.coord=coord
		self.adjacent_edges_to = [] #what edges this junction goes to
		self.adjacent_edges_from = [] # what edges goes to this junction
		self.utility = {}
		self.x = self.coord[0]
		self.y = self.coord[1]
		self.number_players = 0
		self.adjacent_junctions = [] # adjacent junctions can be traveled to
		self.cost = 5

	def __repr__(self):
		return repr((self.junction_id, self.x,self.y))
		



class Map(object):
	def __init__(self, sumo_cfg):
		'''
		load global map traci
		'''
		self.sumo_cfg = sumo_cfg
		self.edges = {}
		self.junctions = {}
		self.complex_row_col = self.populate_edges_junctions()
		
	@staticmethod
	def mps_to_Mph(mps):
		return ((mps * 3600)/1609.34)
		
	@staticmethod
	def get_distance(x2,y2,x1,y1):
		return math.sqrt((x2 - x1)**2+(y2 - y1)**2)

	def populate_edges_junctions(self):
		row_col_dict = {}
		sumo_xml = minidom.parse(self.sumo_cfg)

		map_path = sumo_xml.getElementsByTagName('net-file')[0].attributes['value'].value
		map_path = os.path.join(os.path.dirname(self.sumo_cfg), map_path)

		print('map path is ', map_path)

		doc = minidom.parse(map_path)
		edge_list = [x for x in doc.getElementsByTagName('edge') if not ':' in x.attributes['id'].value]
		junction_list = [x for x in doc.getElementsByTagName('junction') if not ':' in x.attributes['id'].value]

		for item in junction_list:
			junct_id = item.attributes['id'].value
			self.junctions[junct_id] = Junctions((float(item.attributes['x'].value), float(item.attributes['y'].value)), item.attributes['id'].value)

			#print(junct_id)
			row_col_dict[junct_id] = junct_id[4:]

		for item in edge_list:
			self.edges[item.attributes['id'].value] = Edge(item.attributes['from'].value, item.attributes['to'].value, float(item.childNodes[1].attributes['speed'].value), self.calculate_distance(item.attributes['from'].value, item.attributes['to'].value))
			self.junctions[item.attributes['from'].value].adjacent_edges_to.append(item.attributes['id'].value) #takes edge and append it to adjacent edge list of from node
			self.junctions[item.attributes['to'].value].adjacent_edges_from.append(item.attributes['id'].value)
			self.junctions[item.attributes['from'].value].adjacent_junctions.append(item.attributes['to'].value)

		return row_col_dict

	def row_col(self, row, column):
		row_col_dict = {}
		sorted_junctions = sorted(self.junctions.values(), key= attrgetter('y', 'x'), reverse=True)
		assert len(sorted_junctions) == row*column, 'converting map from sumo failed'
		index = 0
		for i in range(row):
			for j in range(column-1, -1, -1):
				row_col_dict[str(i)+'_'+str(j)] = sorted_junctions[index].junction_id
				index+=1

		return row_col_dict


	def calculate_distance(self, junc_from, junc_to):
		return Map.get_distance(self.junctions[junc_to].x, self.junctions[junc_to].y, self.junctions[junc_from].x, self.junctions[junc_from].y)

	

	#o(n^2) need to loop through all the edges that is connected to the node from and to
	
	def find_best_route(self, start, end, weights=False):
		if start == end:
			return
		weight_dict = {} #if weights is required, populate this dic with path weights
		best_route = None
		for start_edge in self.junctions[start].adjacent_edges_to:
			for end_edge in self.junctions[end].adjacent_edges_from:
				current_route = traci.simulation.findRoute(start_edge, end_edge)
				if not best_route:
					best_route = current_route	
				else:
					if current_route.travelTime < best_route.travelTime:
						best_route = current_route

				if weights:
					key_val = self.edges[start_edge]._to
					if key_val in weight_dict:
						weight_dict[key_val] = min(current_route, weight_dict[key_val], key=attrgetter('travelTime'))
					else:
						weight_dict[key_val] = current_route

		if weights:
			return weight_dict, best_route

		return best_route

	def find_adjacent_cells(self, sumo_junction, param='to'):
		adjacent_list = []

		if param == 'to' or param == 'both':
			for edge in self.junctions[sumo_junction].adjacent_edges_to:
				adjacent_list.append(self.edges[edge]._to)

		if param == 'from' or param == 'both':
			for edge in self.junctions[sumo_junction].adjacent_edges_from:
				adjacent_list.append(self.edges[edge]._from)


		return adjacent_list




if __name__ == '__main__':
	pass