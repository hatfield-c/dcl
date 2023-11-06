import numpy as np
import math
import random

import physics.Transform as Transform
import planners.PlannerInterface as PlannerInterface
import entities.SimpleEntity as SimpleEntity

class DiffusionPlanner(PlannerInterface.PlannerInterface):

	def __init__(self, client_id, time_counter, waypoints, waypoint_threshold = 0.5, turn_strength = 1, debug = False):
		self.client_id = client_id
		self.time_counter = time_counter
		self.waypoints = waypoints
		self.waypoint_threshold = waypoint_threshold
		self.turn_strength = turn_strength

		self.current_action = "move"

		self.drop_time = 280

	def GetPlan(self, sensors, metadata):
		telemetry = sensors["telemetry"]
		target_entity = sensors["target"]

		sensor_data = telemetry.ReadSensor(None)

		target_position = target_entity.GetPosition()
		current_position = sensor_data["position"]

		target_offset = target_position - current_position

		current_quat = sensor_data["quaternion"]

		drop_package = False
		if self.drop_time < self.time_counter.GetCount():
			drop_package = True

		plan = {
			"move_action": self.current_action,
			"target_offset": target_offset,
			"rotation": sensor_data["rotation"],
			"velocity": sensor_data["velocity"],
			"angular_velocity": sensor_data["angular_velocity"],
			"drop_package": drop_package,
			# PID Controller data below
			"current_quat": current_quat,
			"current_altitude": current_position[2],
		}

		return plan

	def SetWaypoints(self, new_waypoints):
		pass
