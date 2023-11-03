
class ScenarioFactoryInterface:
	def __init__(self):
		pass

	def Create(self, client_id):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')
