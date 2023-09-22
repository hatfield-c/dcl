import numpy as np
import pybullet as pb

import entities.EntityInterface as EntityInterface

class DynamicObject(EntityInterface.EntityInterface):
	def __init__(
		self,
		urdf_name,
		position = [0, 0 ,0],
		rotation = [0, 0, 0],
		permuters = None
	):
		self.urdf_name = urdf_name
		self.start_position = np.array(position)
		self.start_rotation = np.array(rotation)
		self.permuters = permuters

		rotation_quaternion = pb.getQuaternionFromEuler(self.start_rotation)
		self.pb_id = pb.loadURDF(self.urdf_name, self.start_position, rotation_quaternion)

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

	def SetState(self, state_data):
		if "position" in state_data:
			position = state_data["position"]
			quaternion = self.GetQuaternion()

			if "quaternion" in state_data:
				quaternion = state_data["quaternion"]

			pb.resetBasePositionAndOrientation(self.pb_id, position, quaternion)

		if "velocity" in state_data:
			velocity = state_data["velocity"]
			angular_velocity = np.array([0, 0, 0])

			if "angular_velocity" in state_data:
				angular_velocity = state_data["angular_velocity"]

			pb.resetBaseVelocity(self.pb_id, velocity, angular_velocity)

	def GetStatePermutation(self):
		permutation = {}

		if self.permuters is None:
			return permutation

		for label in self.permuters:
			permuter = self.permuters[label]

			permutation[label] = permuter.GetPermutation()

		return permutation
