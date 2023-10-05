
class ObserverInterface:
	def __init__(self):
		pass
	
	def RegisterEntities(self, entity_list):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')
	
	def Observe(self, timestep):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')