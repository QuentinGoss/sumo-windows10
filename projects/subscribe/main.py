import traci
import traci.constants as tc
from settings import Settings
import os
import sys
from random import choice
sys.path.append("./../")
from traci_env import EnvironmentListener




def start_simulation():

	n_step = 0
	env = EnvironmentListener()

	while True:

		traci.simulationStep()
		traci.addStepListener(env)
		n_step+=1


	traci.close()

if __name__ == '__main__':
	print(traci.__file__)
	traci.start(["sumo-gui", "-c", Settings.sumo_config])
	start_simulation()




