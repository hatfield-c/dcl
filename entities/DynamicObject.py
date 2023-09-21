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

	def SetState(self, data):
		if "position" in data:
			position = data["position"]
			quaternion = np.array([0, 0, 0, 0])

			if "quaternion" in data:
				quaternion = data["quaternion"]

			pb.resetBasePositionAndOrientation(self.pb_id, position, quaternion)
			
		if "velocity" in data:
			velocity = data["velocity"]
			angular_velocity = np.array([0, 0, 0])

			pb.resetBaseVelocity(self.pb_id, velocity, angular_velocity)