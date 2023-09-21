import time
import numpy as np
import pybullet as pb

import entities.agents.AgentInterface as AgentInterface

import actuators.RotorActuator as RotorActuator
import actuators.ArmActuator as ArmActuator
import sensors.TelemetrySensor as TelemetrySensor

class DropDrone(AgentInterface.AgentInterface):
	def __init__(
			self,
			urdf_name,
			position = [0, 0 ,0],
			rotation = [0, 0, 0],
			velocity = [0, 0, 0],
			angular_velocity = [0, 0 ,0],
			planner = None,
			controller = None
		):
		self.urdf_name = urdf_name
		
		self.position = np.array(position)
		self.rotation = np.array(rotation)
		self.velocity = np.array(velocity)
		self.angular_velocity = np.array(angular_velocity)
		
		self.rotors = RotorActuator.RotorActuator()
		self.arm = ArmActuator.ArmActuator(np.array([0, 0, -0.2]))
		self.planner = planner
		self.controller = controller

		self.telem = TelemetrySensor.TelemetrySensor(self)
		
		self.sensors = {
			"telem": self.telem
		}
		rotation_quaternion = pb.getQuaternionFromEuler(self.rotation)
		self.pb_id = pb.loadURDF(self.urdf_name, self.position, rotation_quaternion)
		
		self.metadata = {
			"pb_id": self.pb_id,
			"urdf_name": self.urdf_name
		}
		
		self.drop_timer = time.time()
		
	def TakeAction(self):
		plan = self.planner.GetPlan(self.sensors, self.metadata)
		rotor_control = self.controller.GetControlSignal(plan, self.metadata)
		
		rotor_control["pb_id"] = self.pb_id
		
		if time.time() - self.drop_timer > 3:
			self.drop_timer = time.time()
			
			telem_data = self.telem.ReadSensor(None)
			
			drop_data = {
				"position": telem_data["gps"],
				"velocity": telem_data["velocity"],
				"quaternion": telem_data["quat"]
			}
			
			self.arm.Actuate(drop_data)
		
		self.rotors.Actuate(rotor_control)
		
	def GetSensors(self):
		return self.sensors
	
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
		
	def GetAngularAndLinearVelocity(self):
		velocity, angular_velocity = pb.getBaseVelocity(self.pb_id)
		
		angular_velocity = np.array(angular_velocity)
		velocity = np.array(velocity)
		
		return velocity, angular_velocity
	
	def GetPosition(self):
		position, rotation = self.GetPositionRotation()
		
		return position
	
	def GetRotation(self):
		position, rotation = self.GetPositionRotation()
		
		return rotation
	
	def GetQuaternion(self):
		position, quaternion = pb.getBasePositionAndOrientation(self.pb_id)
		
		return quaternion
	
	def GetAngularVelocity(self):
		velocity, angular_velocity = self.GetAngularAndLinearVelocity()
		 
		return angular_velocity
	
	def GetVelocity(self):
		velocity, angular_velocity = self.GetAngularAndLinearVelocity()
		 
		return velocity
	  
	 