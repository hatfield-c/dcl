import numpy as np
import torch
import math

import CONFIG
import planners.PlannerInterface as PlannerInterface

class PositiveDbPlanner(PlannerInterface.PlannerInterface):

	def __init__(self):
		pdb_raw = np.fromfile(CONFIG.pdb_path, np.float32)
		pdb_raw = pdb_raw.astype(np.float32)
		pdb_raw = pdb_raw.reshape(14093, 6)
		self.pdb = pdb_raw[:, [ 0, 2, 1, 3, 5, 4 ]]

	def GetPlan(self, sensors, metadata):
		telemetry = sensors["telemetry"]
		sensor_data = telemetry.ReadSensor(None)
		
		position = sensor_data["position"]
		rotation = sensor_data["rotation"]
		velocity = sensor_data["velocity"]
		angular_velocity = sensor_data["angular_velocity"]
		
		query = np.concatenate((position, velocity))
		query = np.round(query)
		
		is_drop = False
		for i in range(14093):
			entry = self.pdb[i]
			
			error = np.linalg.norm(entry - query)
			
			if(error < 0.1):
				is_drop = True
		
		plan = {
			"is_dropped": is_drop
		}

		return plan
