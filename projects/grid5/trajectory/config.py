import os
###############################
#      Runner.py Configuration
###############################
# Project name
s_project_name = 'grid4'
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
#      grid4 configuration
###############################

# The properties of our vehicles
#s_vtype = """<vType id="vw_super" accel="0.6" decel="1.3" sigma="0.4" length="5" minGap="2.5" maxSpeed="3" guiShape="passenger"/>"""
