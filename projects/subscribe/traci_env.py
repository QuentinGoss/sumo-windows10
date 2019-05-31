import traci
import traci.constants as tc
from core import initialize, timestep
from env import Environment
#env is for storing data contains map and players



class EnvironmentListener(traci.StepListener):
	def __init__(self):
		super(EnvironmentListener, self).__init__()
		initialize(traci)
		self.sim_env = Environment()
	def step(self, t=0):
		#action performed after each step
		for veh_id in traci.simulation.getDepartedIDList():
			traci.vehicle.subscribe(veh_id, [tc.VAR_POSITION, tc.VAR_SPEED, tc.VAR_EDGES, tc.VAR_ROUTE_INDEX,tc.VAR_ROAD_ID])
		data = traci.vehicle.getAllSubscriptionResults()
		timestep(traci, t)
		self.sim_env.populate_players(data)
		#for key, value in self.sim_env.player_data.items():
			#print(key, value.speed)
			#break
		#print(self.sim_env.player_data)
	

