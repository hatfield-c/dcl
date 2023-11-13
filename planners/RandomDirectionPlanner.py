import numpy as np
import math
import random

import physics.Transform as Transform
import planners.PlannerInterface as PlannerInterface
import entities.SimpleEntity as SimpleEntity

class RandomDirectionPlanner(PlannerInterface.PlannerInterface):

	def __init__(self, client_id, distance_scale, debug = False):
		self.client_id = client_id
		self.distance_scale = distance_scale

		self.current_action = "move"

		self.debug = debug
		self.waypoint_marker = None
		if debug:
			self.waypoint_marker = SimpleEntity.SimpleEntity(
				urdf_name = "entity_files/markers/green_diamond.urdf",
				client_id = self.client_id,
				position = [0, 0, -10],
			)

	def GetPlan(self, sensors, metadata):
		telemetry = sensors["telemetry"]

		sensor_data = telemetry.ReadSensor(None)

		current_position = sensor_data["position"]
		next_position = current_position + (np.random.randn(3) * self.distance_scale)

		if self.debug:
			self.waypoint_marker.SetState({"position": next_position})

		diff = next_position - current_position
		distance = np.linalg.norm(diff)

		if distance == 0:
			distance = 1

		desired_direction = diff / distance

		velocity = sensor_data["velocity"]
		current_quat = sensor_data["quaternion"]

		drop_package = False

		plan = {
			"move_action": self.current_action,
			"current_quat": current_quat,
			"current_altitude": current_position[2],
			"desired_direction": desired_direction,
			"desired_altitude": next_position[2],
			"velocity": velocity,
			"drop_package": drop_package
		}

		return plan

	def SetWaypoints(self, new_waypoints):
		pass
