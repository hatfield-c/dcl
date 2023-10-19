
import entities.EntityInterface as EntityInterface

class AgentInterface(EntityInterface.EntityInterface):
	def __init__(self):
		pass

	def TakeAction(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def GetSensors(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def GetPreviousAction(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')
