
class ScenarioInterface:
	def __init__(self):
		pass

	def InstantiateEntities(self):
		raise NotImplementedError()

	def UpdateEntities(self):
		raise NotImplementedError()

	def UpdateAgents(self):
		raise NotImplementedError()

	def ResetScenario(self):
		raise NotImplementedError()
