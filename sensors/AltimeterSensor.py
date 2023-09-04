import pybullet as pb

import sensors.SensorInterface as SensorInterface

class AltimeterSensor(SensorInterface.SensorInterface):
	def __init__(self, entity):
		self.entity = entity
	
	def ReadSensor(self, control_data):
		position, orientation = self.entity.GetPosition()
		
		return position[2]
		
		