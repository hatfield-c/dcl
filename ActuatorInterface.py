
class ActuatorInterface:
	def __init__(self):
		pass
	
	def Actuate(self, control_data):
		raise NotImplementedError()