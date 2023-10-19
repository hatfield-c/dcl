
class ActuatorInterface:
	def __init__(self):
		pass

	def Actuate(self, control_data):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def GetLastCommand(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')
