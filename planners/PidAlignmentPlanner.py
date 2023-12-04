import time
import numpy as np
import math
import random

import controllers.modules.Pid as Pid
import physics.Transform as Transform
import physics.CubicBezier as CubicBezier
import planners.PlannerInterface as PlannerInterface
import entities.SimpleEntity as SimpleEntity

class PidAlignmentPlanner(PlannerInterface.PlannerInterface):

	def __init__(self, client_id, episode_length, release_planner, debug = False):
		self.client_id = client_id
		self.episode_length = episode_length
		self.step_size = 1 / episode_length

		self.debug = debug
		self.direction_marker = None
		self.marker_offset = 1

		self.align_pid = Pid.Pid(
			p_scale = 1,
			i_scale = 0,
			d_scale = 0.6,
		)

		self.release_planner = release_planner

		if debug:
			self.direction_marker = SimpleEntity.SimpleEntity(
				urdf_name = "entity_files/markers/green_diamond.urdf",
				client_id = self.client_id,
				position = [0, 0, -10],
			)

			self.velocity_marker = SimpleEntity.SimpleEntity(
				urdf_name = "entity_files/markers/purple_diamond.urdf",
				client_id = self.client_id,
				position = [0, 0, -10],
			)

	def GetPlan(self, sensors, metadata):
		telemetry = sensors["telemetry"]
		sensor_data = telemetry.ReadSensor(None)

		current_position = sensor_data["position"]
		velocity = sensor_data["velocity"]
		current_quat = sensor_data["quaternion"]

		lateral_error = current_position[0]# ** 2
		lateral_signal = self.align_pid.ControlStep(lateral_error, 0, velocity[0])

		lateral_signal = np.clip(lateral_signal, -1, 1)
		forward_signal = np.sqrt(1 - (lateral_signal ** 2))

		desired_direction = np.array([lateral_signal, forward_signal])

		desired_altitude = 2.5

		if self.debug:
			desired_dir_debug = np.array([lateral_signal, forward_signal, 0])
			velocity_dir_debug = Transform.GetUnit(velocity)

			direction_marker_position = current_position + (desired_dir_debug * self.marker_offset)
			velocity_marker_position = current_position + (velocity_dir_debug * self.marker_offset)

			self.direction_marker.SetState({"position": direction_marker_position})
			self.velocity_marker.SetState({"position": velocity_marker_position})

		drop_package = self.release_planner.GetPlan(sensors, metadata)

		plan = {
			"move_action": "move",
			"current_quat": current_quat,
			"current_altitude": current_position[2],
			"desired_direction": desired_direction[[0, 1]],
			"desired_altitude": desired_altitude,
			"velocity": velocity,
			"drop_package": drop_package
		}

		return plan

	def SetNewPath(self, control_points):
		pass

	def GetControlPoints(self):
		control_points = np.zeros((4, 1))

		return control_points
