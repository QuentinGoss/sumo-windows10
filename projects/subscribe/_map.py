#when the car moves its always have be aware of its neighboors, need the broadcast to find the naighboor location


#this map class is handled by the server
#to update user map the server handle requests

from xml.dom import minidom
from settings import Settings
import traci

class Edge(object):
	def __init__(self, _from, _to, speed):
		self._from = _from
		self._to = _to
		self.speed = speed
		

class Junctions(object):
	def __init__(self, coord, edge_from):
		#each junction would contain a utility matrix showing 
		self.coord=coord
		self.adjacent_edges_to = []
		self.adjacent_edges_from = edge_from
		self.utility = {}




class Map(object):
	def __init__(self):
		'''
		load global map traci
		'''
		self.edges = {}
		self.junctions = {}
		self.populate_junctions()
		self.populate_edges()
		
	@staticmethod
	def mps_to_Mph(mps):
		return ((mps * 3600)/1609.34)

	def populate_edges(self):
		doc = minidom.parse(Settings.map_path)
		edge_list = [x for x in doc.getElementsByTagName('edge') if not ':' in x.attributes['id'].value]
		junction_list = [x for x in doc.getElementsByTagName('junction') if not ':' in x.attributes['id'].value]

		for item in junction_list:
			self.junctions[item.attributes['id'].value] = Junctions((item.attributes['x'].value, ))


		for item in edge_list:
			self.edges[item.attributes['id'].value] = Edge(item.attributes['from'].value, item.attributes['to'].value, Map.mps_to_Mph(float(item.childNodes[1].attributes['speed'].value)))
			self.junctions[item.attributes['from'].value].adjacent_edges.append(item.attributes['id'].value) #takes edge and append it to adjacent edge list of from node
		#for key, value in self.edges.items():
			#print(value._from, value._to, value.speed)
			#break


	def populate_junctions(self):
		junct =  [x for x in traci.junction.getIDList() if not ':' in x]
		for value in junct:
			self.junctions[value] = Junctions(traci.junction.getPosition(value))
		print('Junctions populate complete, total: ', len(junct))






if __name__ =='__main__':
	my_map = Map.mps_to_Mph(2.4)
	print(my_map)
