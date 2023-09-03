
import sensors.SensorInterface as SensorInterface

class GpsSensor(SensorInterface.SensorInterface):
	def __init__(self, entity):
		self.entity = entity
		
	def ReadSensor(self, control_data):
		return self.entity.GetPosition()