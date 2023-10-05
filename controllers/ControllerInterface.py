
class ControllerInterface:
	def __init__(self):
		pass
	
	def GetControlSignal(self, plan, metadata):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')