
class PlannerInterface:
	def __init__(self):
		pass
	
	def GetPlan(self, sensors, metadata):
		raise NotImplementedError()