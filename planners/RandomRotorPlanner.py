import numpy as np
import math
import random

import physics.Transform as Transform
import planners.PlannerInterface as PlannerInterface
import entities.SimpleEntity as SimpleEntity

class RandomRotorPlanner(PlannerInterface.PlannerInterface):

	def __init__(self, client_id, debug = False):
		self.client_id = client_id

		self.rotor_low = -0.03
		self.rotor_high = 0.27
		self.torque_low = -0.55
		self.torque_high = 0.55

		#debug = True
		self.debug = debug

		self.waypoint_marker = None
		if debug:
			self.waypoint_marker = SimpleEntity.SimpleEntity(
				urdf_name = "entity_files/markers/green_diamond.urdf",
				client_id = self.client_id,
				position = [0, 0, -10],
			)

		self.new_start = True

	def GetPlan(self, sensors, metadata):

		if self.debug and self.new_start:
			self.new_start = False
			telemetry = sensors["telemetry"]
			sensor_data = telemetry.ReadSensor(None)
			current_position = sensor_data["position"]

			self.waypoint_marker.SetState({"position": current_position})

		rotor_signal = np.random.uniform(self.rotor_low, self.rotor_high, 5)
		torque_signal = np.random.uniform(self.torque_low, self.torque_high, 1)[0]

		drop_package = False

		plan = {
			"fr_rotor_force": rotor_signal[0],
			"fl_rotor_force": rotor_signal[1],
			"br_rotor_force": rotor_signal[2],
			"bl_rotor_force": rotor_signal[3],
			"torque": torque_signal,
			"drop_package": drop_package
		}

		return plan

	def ResetStart(self):
		self.new_start = True
