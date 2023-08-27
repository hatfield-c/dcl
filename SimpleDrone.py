import numpy as np
import pybullet as pb

import AgentInterface
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
			actuator = None
		):
		self.urdf_name = urdf_name
		
		self.position = np.array(position)
		self.rotation = np.array(rotation)
		self.velocity = np.array(velocity)
		self.angular_velocity = np.array(angular_velocity)
		
		self.actuator = actuator
		if actuator is None:
			self.actuator = SimpleDroneActuator.SimpleDroneActuator()
		
		self.altimeter = AltimeterSensor.AltimeterSensor()
		
		rotation_quaternion = pb.getQuaternionFromEuler(self.rotation)
		self.pb_id = pb.loadURDF(self.urdf_name, self.position, rotation_quaternion)
		
	def TakeAction(self):
		sensor_control = { "pb_id": self.pb_id }
		
		altitude = self.altimeter.ReadSensor(sensor_control)
		
		force = 0
		if altitude < 0.8:
			force = 0.2
		
		if altitude > 0.8:
			force = 0.06
		
		rotor_control = {
			"pb_id": self.pb_id,
			"fr_rotor_force": force,
			"fl_rotor_force": force,
			"br_rotor_force": force,
			"bl_rotor_force": force
		}
		
		self.actuator.Actuate(rotor_control)