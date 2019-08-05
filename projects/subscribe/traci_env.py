import traci
import traci.constants as tc
from env import Environment
from random import choice
import math
from settings import GraphSetting
#env is for storing data contains map and players
#try to keep all traci calls in here


class EnvironmentListener(traci.StepListener):
	def __init__(self):
		super(EnvironmentListener, self).__init__()
		self.sim_env = Environment()


		self.initial_reward_random(GraphSetting.reward_numbers)
		self.initial_route_random(GraphSetting.car_numbers)
		
		self.junction_sub()
		

	def initial_route_random(self, amount):

		list_edges = list(self.sim_env.map_data.edges)
		list_juncts = list(self.sim_env.map_data.junctions)
		for i in range(amount):
			veh_id = 'veh_'+str(i)
			route_id = 'route_'+str(i)
			#traci.route.add(route_id, [choice(list_edges) for _ in range(2)])	
			#traci.route.add(route_id, [choice(list_edges), '-cell0_0N'])
			end = GraphSetting.destination
			start = choice(list_juncts)
			while start==end: start=choice(list_juncts)
			traci.route.add(route_id, self.sim_env.map_data.find_best_route(start, end).edges)
			traci.vehicle.add(veh_id, route_id, typeID='chevy_s10',departLane='random')
			route = traci.route.getEdges(route_id)
			self.sim_env.add_player(veh_id, route, end)


	def initial_reward_random(self, amount, value=100):
		for i in range(amount):

			id_value = f'poi_{str(i)}'
			junction=choice(list(self.sim_env.map_data.junctions.keys()))

			self.sim_env.rewards_list[junction] = value #reward list is inters of junctions
			self.sim_env.poi_list[id_value]= {}
			self.sim_env.poi_to_junct[id_value] = junction
			traci.poi.add(id_value, *traci.junction.getPosition(junction), color=(255,255,255,0), layer=10, height=10)
			traci.poi.subscribeContext(id_value, tc.CMD_GET_VEHICLE_VARIABLE, 50, [tc.VAR_EDGES, tc.VAR_ROAD_ID])
			print(f'added {id_value} to location {junction}')




	def step(self, t=0):
		#action performed after each step

		self.vehicle_sub()
		#self.sim_env.process_junction()
		self.sim_env.process_poi()



	def vehicle_sub(self):
		for veh_id in traci.vehicle.getIDList():
			traci.vehicle.subscribe(veh_id, [tc.VAR_POSITION, tc.VAR_SPEED, tc.VAR_EDGES, tc.VAR_ROUTE_INDEX,tc.VAR_ROAD_ID])


	def junction_sub(self):
		len_junction = 0
		for junc, junc_obj in self.sim_env.map_data.junctions.items():
			if not ':' in junc:
				dist_from_junc = EnvironmentListener.mean([self.sim_env.map_data.edges[x].distance for x in junc_obj.adjacent_edges_from])
				if dist_from_junc:
					#traci subscribe need to convert miles to meters
					traci.junction.subscribeContext(junc, tc.CMD_GET_VEHICLE_VARIABLE, (dist_from_junc/4)*1609.34, [tc.VAR_EDGES, tc.VAR_ROAD_ID])
					len_junction+=1
		print('len junctions sub to ', len_junction)


		
	@staticmethod
	def mean(list_value):
		if len(list_value) == 0:
			return
		return sum(list_value)/len(list_value)
