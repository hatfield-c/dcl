
class SensorInterface:
	def __init__(self):
		pass
	
	def ReadSensor(self, control_data):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')