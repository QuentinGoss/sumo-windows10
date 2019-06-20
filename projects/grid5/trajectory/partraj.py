# partraj.py
# Author: Quentin Goss
# Last Modified: 6/4/19
#
# Some appraches towards applying our Participant Trajectory Algorithm

# Gets the trajectory of a vehicle and it's current position in it's route.
# @param traci = traci instance
# @param string veh_id = Vehicle ID
# @return [int,(string)] = Index of the vehicle in it's route and the
#                          Tuple of all edge ids in the route
def getTrajectory(traci,veh_id):
    return [traci.vehicle.getRouteIndex(veh_id),traci.vehicle.getRoute(veh_id)]

# Checks if the vehicle is at the end of it's route using index data
# @param int route_index = position in the route
# @param tuple route_tuple = tuple of all edge ids in the route
# @return true or false? If the vehicle is at the last edge of it's route
def isAtDestinationByIndex(route_index,route_tuple):
    if route_index == len(route_tuple) - 1:
        return True
    return False
    
# Checks if te vehicle is at the end of it's route given the vehicle ID
# @param traci = traci instance
# @param string veh_id = Vehicle ID
# @return true or false? If the vehicle is at the last edge of it's route
def isAtDestination(traci,veh_id):
    if traci.vehicle.getRouteIndex(veh_id) == len(traci.vehicle.getRoute(veh_id)) - 1:
        return True
    return False

def getLastElementOfTrajectory(traci,veh_id):
    return
