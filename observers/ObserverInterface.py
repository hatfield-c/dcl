
class ObserverInterface:
	def __init__(self):
		pass
	
	def RegisterEntities(self, entity_list):
		raise NotImplementedError()
	
	def Observe(self, timestep):
		raise NotImplementedError()