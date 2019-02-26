# basicMethods.py
#
# Author: Quentin Goss
#
# Basic SUMO methods

# This is a premade vehicle type.
# In core.py general_elemets, replace the line:
#   return ''
# with:
#   return config.basicMethods.s_vtype
s_vtype = """<vType id="vw_super" accel="0.6" decel="1.3" sigma="1" length="5" minGap="2.5" maxSpeed="3" guiShape="passenger"/>"""

###############################
# Add a vehicle to the simulation
#
# @param traci = traci instance
# @param N_VEHICLES = current number of vehicles
# @param s_route_start = id of the starting route
# @param s_edge_end = id of the sink edge
# @param s_type_id = the vehicle type default(vw_super)
# @param color = color default(silver)
###############################
def add_vehicle(traci,N_VEHICLES,s_route_start,s_edge_end,s_typeID='vw_super',color=(180,180,180)):
  s_veh_id = 'veh' + str(N_VEHICLES)
  traci.vehicle.add(s_veh_id,s_route_start,s_typeID,departLane='random')
  traci.vehicle.changeTarget(s_veh_id,s_edge_end)
  traci.vehicle.setColor(s_veh_id,color)
  return(N_VEHICLES + 1)
# end def add_vehicle():

