
class AgentInterface:
	def __init__(self):
		pass
	
	def TakeAction(self):
		raise NotImplementedError()
		
	def GetSensors(self):
		raise NotImplementedError()