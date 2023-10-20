import time
import numpy as np
import pybullet as pb

import entities.agents.AgentInterface as AgentInterface
import entities.SimpleEntity as SimpleEntity

import actuators.RotorActuator as RotorActuator
import actuators.ArmActuator as ArmActuator
import sensors.TelemetrySensor as TelemetrySensor

class DropDrone(SimpleEntity.SimpleEntity, AgentInterface.AgentInterface):
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
			controller = None,
		):

		super(DropDrone, self).__init__(
			urdf_name = urdf_name,
			position = position,
			rotation = rotation,
			quaternion = quaternion,
			velocity = velocity,
			angular_velocity = angular_velocity,
			permuters = permuters
		)

		self.rotors = RotorActuator.RotorActuator()
		self.arm = ArmActuator.ArmActuator(np.array([0, 0, -0.2]))
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
		rotor_control = self.controller.GetControlSignal(plan, self.metadata)

		rotor_control["pb_id"] = self.pb_id

		if time.time() - self.drop_timer > 3:
			self.drop_timer = time.time()

			drop_data = {
				"position": self.GetPosition(),
				"velocity": self.GetVelocity(),
				"quaternion": self.GetQuaternion()
			}

			self.arm.Actuate(drop_data)

		self.rotors.Actuate(rotor_control)

	def IsPackageDropped(self):
		last_command = self.arm.GetLastCommand()

		if last_command[0] == 0:
			return False

		return True

	def GetPreviousAction(self):
		arm_command = self.arm.GetLastCommand()
		rotor_command = self.rotors.GetLastCommand()

		return np.concatenate((arm_command, rotor_command))

	def SetState(self, state_data):
		super().SetState(state_data)

		if "waypoints" in state_data:
			waypoints = state_data["waypoints"]

			self.planner.SetWaypoints(waypoints)

	def GetSensors(self):
		return self.sensors

	def GetPackageEntity(self):
		return self.arm.package
