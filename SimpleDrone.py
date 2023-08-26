import numpy as np
import pybullet as pb

import EntityInterface
import SimpleDroneActuator
import AltimeterSensor

class SimpleDrone(EntityInterface.EntityInterface):
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
		if altitude < 0.5:
			force = 0.5
		
		if altitude > 1:
			force = 0.067
		
		rotor_control = {
			"pb_id": self.pb_id,
			"fr_rotor_force": force,
			"fl_rotor_force": force,
			"br_rotor_force": force,
			"bl_rotor_force": force
		}
		
		self.actuator.Actuate(rotor_control)