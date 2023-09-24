import numpy as np
import pybullet as pb

import entities.SimpleEntity as SimpleEntity
import entities.agents.AgentInterface as AgentInterface

import actuators.RotorActuator as RotorActuator
import sensors.TelemetrySensor as TelemetrySensor

class SimpleDrone(SimpleEntity.SimpleEntity, AgentInterface.AgentInterface):
	def __init__(
			self,
			urdf_name,
			position = [0, 0 ,0],
			rotation = [0, 0, 0],
			quaternion = None,
			velocity = [0, 0, 0],
			angular_velocity = [0, 0 ,0],
			permuters = None,
			planner = None,
			controller = None
		):
		super(SimpleDrone, self).__init__(urdf_name, position, rotation, quaternion, velocity, angular_velocity, permuters)

		self.rotors = RotorActuator.RotorActuator()
		self.planner = planner
		self.controller = controller

		self.telemetry = TelemetrySensor.TelemetrySensor(self)

		self.sensors = {
			"telemetry": self.telemetry
		}

		self.metadata = {
			"pb_id": self.pb_id,
			"urdf_name": self.urdf_name
		}

		self.metadata = {
			"pb_id": self.pb_id,
			"urdf_name": self.urdf_name
		}

	def TakeAction(self):
		plan = self.planner.GetPlan(self.sensors, self.metadata)
		rotor_control = self.controller.GetControlSignal(plan, self.metadata)

		rotor_control["pb_id"] = self.pb_id

		self.rotors.Actuate(rotor_control)

	def GetSensors(self):
		return self.sensors
