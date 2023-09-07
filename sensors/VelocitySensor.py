
import sensors.SensorInterface as SensorInterface

class VelocitySensor(SensorInterface.SensorInterface):
	def __init__(self, entity):
		self.entity = entity
		
	def ReadSensor(self, control_data):
		return self.entity.GetVelocity()