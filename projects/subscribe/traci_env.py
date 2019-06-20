import traci
import traci.constants as tc
from env import Environment
from random import choice
import math
#env is for storing data contains map and players
#try to keep all traci calls in here


class EnvironmentListener(traci.StepListener):
	def __init__(self):
		super(EnvironmentListener, self).__init__()
		self.sim_env = Environment()

		self.initial_route_random(1)
		self.junction_sub()
		

	def initial_route_random(self, amount):

		list_edges = list(self.sim_env.map_data.edges)
		for i in range(amount):
			veh_id = 'veh_'+str(i)
			route_id = 'route_'+str(i)
			traci.route.add(route_id, [choice(list_edges) for _ in range(2)])
			traci.vehicle.add(veh_id, route_id, typeID='chevy_s10',departLane='random')
			route = traci.route.getEdges(route_id)
			self.sim_env.add_player(veh_id, route)


	def step(self, t=0):
		#action performed after each step

		self.vehicle_sub()
		self.sim_env.process_junction()



	def vehicle_sub(self):
		for veh_id in traci.vehicle.getIDList():
			traci.vehicle.subscribe(veh_id, [tc.VAR_POSITION, tc.VAR_SPEED, tc.VAR_EDGES, tc.VAR_ROUTE_INDEX,tc.VAR_ROAD_ID])


	def junction_sub(self):
		for junc, junc_obj in self.sim_env.map_data.junctions.items():
			if not ':' in junc:
				dist_from_junc = EnvironmentListener.mean([self.sim_env.map_data.edges[x].distance for x in junc_obj.adjacent_edges_from])
				if dist_from_junc:
					traci.junction.subscribeContext(junc, tc.CMD_GET_VEHICLE_VARIABLE, dist_from_junc/4, [tc.VAR_EDGES, tc.VAR_ROAD_ID])
	@staticmethod
	def mean(list_value):
		if len(list_value) == 0:
			return
		return sum(list_value)/len(list_value)
