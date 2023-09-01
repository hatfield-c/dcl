
import entities.EntityInterface as EntityInterface

class AgentInterface(EntityInterface.EntityInterface):
	def __init__(self):
		pass
	
	def TakeAction(self):
		raise NotImplementedError()
		
	def GetSensors(self):
		raise NotImplementedError()