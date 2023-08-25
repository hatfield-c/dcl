import numpy as np
import pybullet as pb

import EntityInterface

class SimpleDrone(EntityInterface.EntityInterface):
	def __init__(
			self,
			urdf_name,
			position = [0, 0 ,0],
			rotation = [0, 0, 0],
			velocity = [0, 0, 0],
			angular_velocity = [0, 0 ,0]
		):
		self.urdf_name = urdf_name
		
		self.position = np.array(position)
		self.rotation = np.array(rotation)
		self.velocity = np.array(velocity)
		self.angular_velocity = np.array(angular_velocity)
		
		rotation_quaternion = pb.getQuaternionFromEuler(self.rotation)
		self.pb_id = pb.loadURDF(self.urdf_name, self.position, rotation_quaternion)