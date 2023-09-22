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

		state_data = {
			"velocity": velocity,
			"angular_velocity": angular_velocity
		}

		self.SetState(state_data)

	def GetBulletId(self):
		return self.pb_id

	def GetUrdf(self):
		return self.urdf_name

	def GetPositionRotation(self):
		position, rotation = pb.getBasePositionAndOrientation(self.pb_id)
		rotation = pb.getEulerFromQuaternion(rotation)

		position = np.array(position)
		rotation = np.array(rotation)

		return position, rotation

	def GetPosition(self):
		position, rotation = self.GetPositionRotation()

		return position

	def GetRotation(self):
		position, rotation = self.GetPositionRotation()

		return rotation

	def GetQuaternion(self):
		position, quaternion = pb.getBasePositionAndOrientation(self.pb_id)

		return quaternion

	def GetAngularAndLinearVelocity(self):
		angular_velocity, velocity = pb.getBaseVelocity(self.pb_id)

		angular_velocity = np.array(angular_velocity)
		velocity = np.array(velocity)

		return angular_velocity, velocity

	def GetAngularVelocity(self):
		angular_velocity, velocity = self.GetAngularAndLinearVelocity()

		return angular_velocity

	def GetVelocity(self):
		 angular_velocity, velocity = self.GetAngularAndLinearVelocity()

		 return velocity

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

			if "angle" in state_data:
				angle = state_data["angle"]

				quaternion = pb.getQuaternionFromEuler(angle)

			if "quaternion" in state_data:
				quaternion = state_data["quaternion"]

			pb.resetBasePositionAndOrientation(self.pb_id, position, quaternion)

		if "velocity" in state_data or "angular_velocity" in state_data:
			velocity = self.GetVelocity()
			angular_velocity = self.GetAngularVelocity()

			if "velocity" in state_data:
				velocity = state_data["velocity"]

			if "angular_velocity" in state_data:
				angular_velocity = state_data["angular_velocity"]

			pb.resetBaseVelocity(self.pb_id, velocity, angular_velocity)
