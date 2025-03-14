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
			client_id,
			position = [0, 0 ,0],
			rotation = [0, 0, 0],
			quaternion = None,
			velocity = [0, 0, 0],
			angular_velocity = [0, 0 ,0],
			permuters = None,
			planner = None,
			controller = None,
			target_entity = None,
		):

		super(DropDrone, self).__init__(
			urdf_name = urdf_name,
			client_id = client_id,
			position = position,
			rotation = rotation,
			quaternion = quaternion,
			velocity = velocity,
			angular_velocity = angular_velocity,
			permuters = permuters
		)

		self.rotors = RotorActuator.RotorActuator(self.client_id)
		self.arm = ArmActuator.ArmActuator(self.client_id, np.array([0, 0, -0.2]))
		self.planner = planner
		self.controller = controller
		self.target_entity = target_entity

		self.telemetry = TelemetrySensor.TelemetrySensor(self)

		self.sensors = {
			"telemetry": self.telemetry,
			"target": self.target_entity
		}

		self.metadata = {
			"pb_id": self.pb_id,
			"urdf_name": self.urdf_name
		}

	def TakeAction(self):
		plan = self.planner.GetPlan(self.sensors, self.metadata)
		control_data = self.controller.GetControlSignal(plan, self.metadata)
		
		control_data["pb_id"] = self.pb_id

		if control_data["drop_package"]:
			drop_data = {
				"position": self.GetPosition(),
				"velocity": self.GetVelocity(),
				"quaternion": self.GetQuaternion()
			}

			self.arm.Actuate(drop_data)

		self.rotors.Actuate(control_data)

	def IsPackageDropped(self):
		last_command = self.arm.GetLastCommand()

		if last_command[0] == 0:
			return False

		return True

	def GetPreviousAction(self):
		#arm_command = self.arm.GetLastCommand()
		rotor_command = self.rotors.GetLastCommand()

		#return np.concatenate((arm_command, rotor_command))
		return rotor_command

	def SetState(self, state_data):
		super().SetState(state_data)

		if "reset_package" in state_data:
			self.arm.Reset()

		if "waypoints" in state_data:
			waypoints = state_data["waypoints"]

			self.planner.SetWaypoints(waypoints)

		if "start_position" in state_data:
			self.planner.ResetStart()

		if "bezier_path" in state_data:
			bezier_path = state_data["bezier_path"]

			self.planner.SetNewPath(bezier_path)

		if "hit_poly" in state_data:
			new_state = state_data["hit_poly"]

			super().SetState(new_state)

	def ApplyDrag(self):
		drag_coefficient = 0.01
		velocity = self.GetVelocity()
		drag_force = -velocity * drag_coefficient
		drone_position = self.GetPosition()

		#print(drag_force)
		#print(velocity)
		#input()

		pb.applyExternalForce(
			self.GetBulletId(),
			-1,
			forceObj = drag_force,
			posObj = drone_position,#[0, 0, 0],
			flags = pb.WORLD_FRAME,#pb.LINK_FRAME,
			physicsClientId = self.client_id
		)


	def GetSensors(self):
		return self.sensors

	def GetPackageEntity(self):
		return self.arm.package

	def GetCameraPosition(self):
		if self.IsPackageDropped():
			return self.arm.package.GetPosition()

		return self.GetPosition()
