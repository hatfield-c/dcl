
class SensorInterface:
	def __init__(self):
		pass
	
	def ReadSensor(self, control_data):
		raise NotImplementedError()