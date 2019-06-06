# Add imports here
import config # ./config.py
import partraj as pta # Participent Trajectory Algorithm

###############################
# Add element(s) to routefiles
#
# @return string = The elements that will be added to the
# routefile.
###############################
def generate_elements():
    
    return ''
# End def generate_elements()


###############################
# Initilize anything that needs to happen at step 0 here.
###############################
def initialize(traci):
    # Add a vehicle
    traci.route.add('route1',['gneE533','-gneE563'])
    traci.vehicle.add('veh0','route1')
    return
# end def intialize


###############################
# Anything that happens within the TraCI control loop goes here.
# One pass of the loop == 1 timestep.
###############################
def timestep(traci,n_step):
    pause()
    return
# end timestep

###############################
# A quick pause
###############################
def pause():
    input("Press return to continue...")
# end def pause()

def test():
    #index,route = pta.getTrajectory(traci,'veh0')
    #print()
    #print(index)
    #print(type(route))
    #if pta.isAtDestination(index,route):
    #    print([index,len(route)])
    #    print("At destination")
    #if pta.isAtDestination(traci,'veh0'):
        #print([index,len(route)])
    #    print("At destination")
