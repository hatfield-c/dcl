import numpy as np
import pybullet as pb

import entities.EntityInterface as EntityInterface

class DynamicObject(EntityInterface.EntityInterface):
	def __init__(
		self,
		urdf_name,
		position = [0, 0 ,0],
		rotation = [0, 0, 0],
	):
		self.urdf_name = urdf_name
		self.start_position = np.array(position)
		self.start_rotation = np.array(rotation)
	
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
	