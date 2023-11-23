import numpy as np
import math
import random

import physics.Transform as Transform
import planners.PlannerInterface as PlannerInterface
import entities.SimpleEntity as SimpleEntity

class BezierPlanner(PlannerInterface.PlannerInterface):

	def __init__(self, client_id, control_points, episode_length, debug = False):
		self.client_id = client_id
		self.episode_length = episode_length
		self.step_size = 1 / episode_length

		self.control_points = control_points
		self.interpolation = 0
		self.altitude_offset = 1

		self.debug = debug
		self.direction_marker = None
		self.marker_offset = 1

		if debug:
			self.path_marker = SimpleEntity.SimpleEntity(
				urdf_name = "entity_files/markers/teal_diamond.urdf",
				client_id = self.client_id,
				position = [0, 0, -10],
			)

			self.direction_marker = SimpleEntity.SimpleEntity(
				urdf_name = "entity_files/markers/green_diamond.urdf",
				client_id = self.client_id,
				position = [0, 0, -10],
			)



	def GetPlan(self, sensors, metadata):
		telemetry = sensors["telemetry"]
		sensor_data = telemetry.ReadSensor(None)

		current_position = sensor_data["position"]
		velocity = sensor_data["velocity"]
		current_quat = sensor_data["quaternion"]

		a0 = self.control_points[0]
		a1 = self.control_points[1]
		a2 = self.control_points[2]
		t = self.interpolation

		path_position = a1 + ((1 - t) ** 2) * (a0 - a1) + (t ** 2) * (a2 - a1)

		diff = path_position - current_position
		distance = np.linalg.norm(diff)

		if distance == 0:
			distance = 1

		desired_direction = diff / distance

		desired_altitude = current_position + (desired_direction * self.altitude_offset)
		desired_altitude = desired_altitude[2]

		if self.debug:
			direction_magnitude = np.linalg.norm(desired_direction)

			if direction_magnitude == 0:
				direction_magnitude = 1

			direction_unit = desired_direction / direction_magnitude

			marker_position = current_position + (direction_unit * self.marker_offset)

			self.path_marker.SetState({"position": path_position})
			self.direction_marker.SetState({"position": marker_position})

		drop_package = False

		plan = {
			"move_action": "move",
			"current_quat": current_quat,
			"current_altitude": current_position[2],
			"desired_direction": desired_direction[[0, 1]],
			"desired_altitude": desired_altitude,
			"velocity": velocity,
			"drop_package": drop_package
		}

		self.interpolation += self.step_size

		return plan

	def SetNewPath(self, control_points):

		if len(control_points.shape) == 1:
			control_points = control_points.reshape(3, 3)

		self.control_points = control_points
		self.interpolation = 0
