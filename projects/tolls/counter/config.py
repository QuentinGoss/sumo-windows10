import os
###############################
#      Runner.py Configuration
###############################
# Project name
s_project_name = 'tolls'
# Length of simulation
n_time_steps = 10000

# If you're using the template and SUMO is installed to the default
# location then don't edit these.
s_absolute_path = os.path.dirname(os.path.abspath(__file__))
s_sumo_tools_dir = 'C:/Program Files (x86)/Eclipse/Sumo/tools'
s_route_file = s_absolute_path + "/../data/" + s_project_name + ".rou.xml"
s_sumocfg_file = s_absolute_path + "/../data/" + s_project_name + ".sumocfg"
s_net_file = s_absolute_path + "/../data/" + s_project_name + ".net.xml"


###############################
#      tolls configuration
###############################

# Random Seed
n_seed = 473

# vehicle type
s_vtype = """<vType id="vw_super" accel="0.6" decel="1.3" sigma="0.4" length="5" minGap="2.5" maxSpeed="3" guiShape="passenger"/>"""

# Maximum number of vehicles in the simulation
n_vehicles_max = 100

# Trough Traffic Initial Route names
ls_ttir = ['Northbound','Southbound']

# Through Traffic Spawn Rate (by Tick)
class ttsr:
  north = 3
  south = 3
  rate = [north,south]

# Edge IDS of map spawns
class spawn:
  north = "-gneE33"
  south = "-gneE144"
  ids = [north,south]

# Edge IDS of map sinks
class sink:
  north = "gneE33"
  south = "gneE144"
  green_nb = "gneE85"
  green_sb = "gneE88"
  blue_nb = "gneE103"
  blue_sb = "gneE101"
  orange_nb = "gneE121"
  orange_sb = "gneE119"
  ids = [north,south,green_nb,green_sb,blue_nb,blue_sb,orange_nb,orange_sb]

# Probablities of visiting each sink from a spawn
# [north,south,green_nb,green_sb,blue_nb,blue_sb,orange_nb,orange_sb]
class prob_sink:
  north = [0.05,0.65,0.05,0.05,0.05,0.05,0.05,0.05]
  south = [0.65,0.05,0.05,0.05,0.05,0.05,0.05,0.05]
  prob = [north,south]
  
# Toll road begin
class toll_road_begin:
  north = "gneE5"
  south = "-gneE125"
  ids = [north,south]
  

