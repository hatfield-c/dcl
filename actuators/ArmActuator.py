import numpy as np

import physics.Transform as Transform
import entities.SimpleEntity as SimpleEntity
import actuators.ActuatorInterface as ActuatorInterface

class ArmActuator(ActuatorInterface.ActuatorInterface):
	def __init__(
		self,
		offset = [0, 0, -1],
		package_urdf = "entity_files/sphere_red.urdf"
	):
		self.offset = offset
		self.offset_distance = np.linalg.norm(self.offset)

		magnitude = self.offset_distance
		if magnitude == 0:
			magnitude = 1

		self.offset_direction = self.offset / magnitude

		self.package = SimpleEntity.SimpleEntity(package_urdf)

	def Actuate(self, control_data):

		position = control_data["position"]
		quaternion = control_data["quaternion"]
		velocity = control_data["velocity"]

		drop_direction = Transform.RotateDirection(quaternion, self.offset_direction)
		drop_offset = drop_direction * self.offset_distance
		drop_position = position + drop_offset

		drop_state = {
			"position": drop_position,
			"quaternion": quaternion,
			"velocity": velocity,
		}

		self.package.SetState(drop_state)
