
class PlannerInterface:
	def __init__(self):
		pass
	
	def GetPlan(self, sensors, metadata):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')