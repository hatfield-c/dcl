
class ScenarioInterface:
	def __init__(self):
		pass

	def InstantiateEntities(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def UpdateEntities(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def UpdateAgents(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def ResetScenario(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')
