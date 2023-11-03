import time
import numpy as np
import pybullet as pb

import entities.agents.AgentInterface as AgentInterface
import entities.SimpleEntity as SimpleEntity

import actuators.RotorActuator as RotorActuator
import actuators.ArmActuator as ArmActuator
import sensors.TelemetrySensor as TelemetrySensor

class TeleopDrone(SimpleEntity.SimpleEntity, AgentInterface.AgentInterface):
	def __init__(
			self,
			urdf_name,
			client_id,
			position = [0, 0 ,0],
			rotation = [0, 0, 0],
			quaternion = None,
			velocity = [0, 0, 0],
			angular_velocity = [0, 0 ,0],
			permuters = None,
			planner = None,
			controller = None
		):
		super(TeleopDrone, self).__init__(urdf_name, client_id, position, rotation, quaternion, velocity, angular_velocity, permuters)

		self.rotors = RotorActuator.RotorActuator(client_id)
		self.arm = ArmActuator.ArmActuator(client_id, np.array([0, 0, -0.2]))
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

		self.drop_timer = time.time()

	def TakeAction(self):
		plan = self.planner.GetPlan(self.sensors, self.metadata)
		rotor_control = self.controller.GetControlSignal(plan, self.sensors)

		rotor_control["pb_id"] = self.pb_id
		'''
		if time.time() - self.drop_timer > 3:
			self.drop_timer = time.time()

			drop_data = {
				"position": self.GetPosition(),
				"velocity": self.GetVelocity(),
				"quaternion": self.GetQuaternion()
			}

			self.arm.Actuate(drop_data)
        '''
		self.rotors.Actuate(rotor_control)
	def RollRight(self):
		print("roll right")

	def RollLeft(self):
		print("roll left")

	def PitchForward(self):
		print("pitch forward")

	def PitchBackwards(self):
		print("pitch backward")

	def YawRight(self):
		print("yawright")

	def YawLeft(self):
		print("yawleft")

	def ThrustUp(self):
		print("thrust up")

	def GetSensors(self):
		return self.sensors
