import numpy as np
import pybullet as pb

class DynamicObject:
	def __init__(
		self,
		urdf_name,
		position = [0, 0 ,0],
		rotation = [0, 0, 0],
	):
		self.urdf_name = urdf_name
		self.position = np.array(position)
		self.rotation = np.array(rotation)
	
		rotation_quaternion = pb.getQuaternionFromEuler(self.rotation)
		self.pb_id = pb.loadURDF(self.urdf_name, self.position, rotation_quaternion)