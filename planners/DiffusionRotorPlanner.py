import numpy as np
import math
import random

import physics.Transform as Transform
import planners.PlannerInterface as PlannerInterface
import entities.SimpleEntity as SimpleEntity

class DiffusionRotorPlanner(PlannerInterface.PlannerInterface):

	def __init__(self, client_id, time_counter):
		self.client_id = client_id
		self.time_counter = time_counter

	def GetPlan(self, sensors, metadata):
		telemetry = sensors["telemetry"]
		target_entity = sensors["target"]

		sensor_data = telemetry.ReadSensor(None)

		target_position = target_entity.GetPosition()
		current_position = sensor_data["position"]

		target_offset = target_position - current_position

		drop_package = True

		plan = {
			"target_offset": target_offset,
			"rotation": sensor_data["rotation"],
			"velocity": sensor_data["velocity"],
			"angular_velocity": sensor_data["angular_velocity"],
			"drop_package": drop_package,
		}

		return plan

	def ResetStart(self):
		pass
