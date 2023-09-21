import numpy as np
import pybullet as pb

import entities.EntityInterface as EntityInterface

class StaticObject(EntityInterface.EntityInterface):
	def __init__(
		self,
		urdf_name,
		position = [0, 0 ,0],
		rotation = [0, 0, 0]
	):
		self.urdf_name = urdf_name
		self.position = np.array(position)
		self.rotation = np.array(rotation)
	
		rotation_quaternion = pb.getQuaternionFromEuler(self.rotation)
		self.pb_id = pb.loadURDF(self.urdf_name, self.position, rotation_quaternion)
		
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