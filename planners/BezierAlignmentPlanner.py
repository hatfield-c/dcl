import time
import numpy as np
import math
import random

import physics.Transform as Transform
import physics.CubicBezier as CubicBezier
import planners.PlannerInterface as PlannerInterface
import entities.SimpleEntity as SimpleEntity

class BezierAlignmentPlanner(PlannerInterface.PlannerInterface):

	def __init__(self, client_id, control_points, episode_length, debug = False):
		self.client_id = client_id
		self.episode_length = episode_length
		self.step_size = 1 / episode_length

		self.bezier_curve = CubicBezier.CubicBezier(control_points[0], control_points[1], control_points[2], control_points[3])
		self.interpolation = 0
		self.altitude_offset = 1

		self.debug = debug
		self.direction_marker = None
		self.marker_offset = 1
		self.alignment = 1

		if debug:
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

		velocity_magnitude = np.linalg.norm(velocity)

		if self.interpolation == 0:
			if velocity[0] > 0 or (velocity_magnitude == 0 and current_position[0] > 0):
				self.alignment = -1

		path_position = self.bezier_curve.GetPosition(self.interpolation)

		lateral_signal = self.alignment * path_position[0]

		lateral_signal = np.clip(lateral_signal, -1, 1)
		forward_signal = np.sqrt(1 - (lateral_signal ** 2))

		desired_direction = np.array([lateral_signal, forward_signal])

		#desired_altitude = current_position + (desired_direction * self.altitude_offset)
		desired_altitude = 1.5#desired_altitude[2]

		if self.debug:
			desired_dir_debug = np.array([lateral_signal, forward_signal, 0])
			marker_position = current_position + (desired_dir_debug * self.marker_offset)

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
			control_points = control_points.reshape(4, 3)

		self.bezier_curve.SetPath(control_points[0], control_points[1], control_points[2], control_points[3])
		self.alignment = 1
		self.interpolation = 0

	def GetControlPoints(self):
		control_points = self.bezier_curve.GetControlPoints()
		control_points = np.array(control_points)

		return control_points
