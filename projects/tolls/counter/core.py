# Add imports here
import config # ./config.py
import spawn
import random

###############################
# Add element(s) to routefiles
#
# @return string = The elements that will be added to the
# routefile.
###############################
def generate_elements():
    s_elements = "\t" + config.s_vtype + "\n"
    return s_elements
# End def generate_elements()


###############################
# Initilize anything that needs to happen at step 0 here.
###############################
def initialize(traci):
    global N_VEHICLES
    N_VEHICLES = 0
    
    global L_VEH
    L_VEH = []
  
    # Add the initial through traffic routes
    for i in range(len(config.ttsr.rate)):
      print(config.ls_ttir[i])
      traci.route.add(config.ls_ttir[i],[config.spawn.ids[i]])
    # end for
    return
# end def intialize


###############################
# Anything that happens within the TraCI control loop goes here.
# One pass of the loop == 1 timestep.
###############################
def timestep(traci,n_step):
    # East to West
    global N_VEHICLES
    N_VEHICLES = spawn.spawn_tts(traci,n_step,N_VEHICLES,random)
    return
# end timestep

###############################
# A quick pause
###############################
def pause():
    input("Press return to continue...")
# end def pause()
