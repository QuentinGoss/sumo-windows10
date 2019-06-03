import traci
import traci.constants as tc
from env import Environment
import random
#env is for storing data contains map and players



class EnvironmentListener(traci.StepListener):
	def __init__(self):
		super(EnvironmentListener, self).__init__()
		self.sim_env = Environment()
		self.sim_env.initial()
	def step(self, t=0):
		#action performed after each step
		#for junction_id in traci.junction.getIDList():
			#traci.junction.subscribe(junction_id, [tc.VAR_WAITING_TIME])

		for veh_id in traci.vehicle.getIDList():
			traci.vehicle.subscribe(veh_id, [tc.VAR_POSITION, tc.VAR_SPEED, tc.VAR_EDGES, tc.VAR_ROUTE_INDEX,tc.VAR_ROAD_ID])
		data = traci.vehicle.getAllSubscriptionResults()
		self.sim_env.populate_players(data)
		#print(data)
		#for key, value in self.sim_env.player_data.items():
			#print(key, value.speed)
			#break
		#print(self.sim_env.player_data)
	
	

