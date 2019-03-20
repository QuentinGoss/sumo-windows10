# toll.py
import config

class vehicle:
  toll_time = []
  def __init__(self, _id):
    self._id = _id
  def record_time(self,n_timestep):
      self.toll_time.append(n_timestep)
      
def update_vehicles(traci,n_step,L_VEH):
  ls_veh_ids = traci.vehicle.getIDList()
  
  # Entering toll road
  for s_veh_id in ls_veh_ids:
    if traci.vehicle.getRoadID(s_veh_id) in config.toll_road_begin.ids and not s_veh_id in L_VEH:
      veh = vehicle(s_veh_id)
      veh.record_time(n_step)
      L_VEH.append(veh)
      
  # Exit destination
