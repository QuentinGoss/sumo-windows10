Extends the usefullness of the POIs in Traci. To use this module, copy over the files in this directory to your project folder and then import the module.

import advancedpoi as apoi

#####################################
# Adding POIS Quickly Using poi.hot #
#####################################

Add the function call:

apoi.initialize(traci)

to the initialization step and pass in the traci instance. Likewise, add the funtion call:

apoi.timestep(traci)

where the timesteps happen. This will all the use of:

poi.hot

For adding POIs to the SUMO simulation simply and easily. Below is an example usage of the hotfile functionality which creates POIs of type sink of the color red at points 15.3,14.2 and 12.9,18.0.

"Sink"
(255,0,0)
15.3,14.2
12.9,18.0



