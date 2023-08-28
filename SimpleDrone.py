import numpy as np
import pybullet as pb

import AgentInterface
import SimpleController
import SimplePlanner
import SimpleDroneActuator
import AltimeterSensor

class SimpleDrone(AgentInterface.AgentInterface):
	def __init__(
			self,
			urdf_name,
			position = [0, 0 ,0],
			rotation = [0, 0, 0],
			velocity = [0, 0, 0],
			angular_velocity = [0, 0 ,0],
			actuator = None,
			planner = None,
			controller = None
		):
		self.urdf_name = urdf_name
		
		self.position = np.array(position)
		self.rotation = np.array(rotation)
		self.velocity = np.array(velocity)
		self.angular_velocity = np.array(angular_velocity)
		
		self.actuator = actuator
		self.planner = planner
		self.controller = controller
		
		if actuator is None:
			self.actuator = SimpleDroneActuator.SimpleDroneActuator()
		
		if self.planner is None:
			self.planner = SimplePlanner.SimplePlanner()
			
		if self.controller is None:
			self.controller = SimpleController.SimpleController()
		
		self.altimeter = AltimeterSensor.AltimeterSensor()
		
		self.sensors = {
			"altimeter": self.altimeter
		}
		
		rotation_quaternion = pb.getQuaternionFromEuler(self.rotation)
		self.pb_id = pb.loadURDF(self.urdf_name, self.position, rotation_quaternion)
		
		self.metadata = {
			"pb_id": self.pb_id,
			"urdf_name": self.urdf_name
		}
		
	def TakeAction(self):
		plan = self.planner.GetPlan(self.sensors, self.metadata)
		rotor_control = self.controller.GetControlSignal(plan, self.metadata)
		
		self.actuator.Actuate(rotor_control)
		
	def GetSensors(self):
		return self.sensors