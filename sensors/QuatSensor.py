
import sensors.SensorInterface as SensorInterface

class QuatSensor(SensorInterface.SensorInterface):
	def __init__(self, entity):
		self.entity = entity
		
	def ReadSensor(self, control_data):
		return self.entity.GetQuaternion()