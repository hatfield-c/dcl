import numpy as np
import pybullet as pb

import entities.EntityInterface as EntityInterface

class SimpleEntity(EntityInterface.EntityInterface):
	def __init__(
		self,
		urdf_name,
		position = [0, 0 ,0],
		rotation = [0, 0, 0],
		quaternion = None,
		velocity = [0, 0, 0],
		angular_velocity = [0, 0 ,0],
		is_static = False,
		permuters = None
	):
		self.urdf_name = urdf_name
		self.permuters = permuters

		if quaternion is None:
			quaternion = pb.getQuaternionFromEuler(rotation)

		if is_static:
			is_static = 1
		else:
			is_static = 0

		self.pb_id = pb.loadURDF(self.urdf_name, position, quaternion, useFixedBase = is_static)

		self.state_data = {
			"position": None,
			"rotation": None,
			"quaternion": None,
			"velocity": None,
			"angular_velocity": None
		}

		velocity_data = {
			"velocity": velocity,
			"angular_velocity": angular_velocity
		}

		self.SetState(velocity_data)
		self.UpdateEntity()

	def UpdateEntity(self):
		position, quaternion = pb.getBasePositionAndOrientation(self.pb_id)
		velocity, angular_velocity = pb.getBaseVelocity(self.pb_id)
		rotation = pb.getEulerFromQuaternion(quaternion)

		self.state_data["position"] = np.array(position)
		self.state_data["quaternion"] = np.array(quaternion)
		self.state_data["velocity"] = np.array(velocity)
		self.state_data["angular_velocity"] = np.array(angular_velocity)
		self.state_data["rotation"] = np.array(rotation)

	def GetBulletId(self):
		return self.pb_id

	def GetUrdf(self):
		return self.urdf_name

	def GetPosition(self):
		return self.state_data["position"]

	def GetRotation(self):
		return self.state_data["rotation"]

	def GetQuaternion(self):
		return self.state_data["quaternion"]

	def GetAngularVelocity(self):
		return self.state_data["angular_velocity"]

	def GetVelocity(self):
		 return self.state_data["velocity"]

	def GetStatePermutation(self):
		permutation = {}

		if self.permuters is None:
			return permutation

		for label in self.permuters:
			permuter = self.permuters[label]

			permutation[label] = permuter.GetPermutation()

		return permutation

	def SetState(self, state_data):

		if "position" in state_data or "quaternion" in state_data or "angle" in state_data:
			position = self.GetPosition()
			quaternion = self.GetQuaternion()

			if "position" in state_data:
				position = state_data["position"]

			if "rotation" in state_data:
				rotation = state_data["rotation"]

				quaternion = pb.getQuaternionFromEuler(rotation)

			if "quaternion" in state_data:
				quaternion = state_data["quaternion"]

			self.state_data["position"] = position
			self.state_data["quaternion"] = quaternion
			self.state_data["rotation"] = pb.getEulerFromQuaternion(quaternion)

			pb.resetBasePositionAndOrientation(self.pb_id, position, quaternion)

		if "velocity" in state_data or "angular_velocity" in state_data:
			velocity = self.GetVelocity()
			angular_velocity = self.GetAngularVelocity()

			if "velocity" in state_data:
				velocity = state_data["velocity"]

			if "angular_velocity" in state_data:
				angular_velocity = state_data["angular_velocity"]

			self.state_data["velocity"] = velocity
			self.state_data["angular_velocity"] = angular_velocity

			pb.resetBaseVelocity(self.pb_id, velocity, angular_velocity)
