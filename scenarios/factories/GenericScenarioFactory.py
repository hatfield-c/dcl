
import scenarios.factories.ScenarioFactoryInterface as ScenarioFactoryInterface

class GenericScenarioFactory(ScenarioFactoryInterface.ScenarioFactoryInterface):
	def __init__(
		self,
		scenario_class
	):
		self.scenario_class = scenario_class

	def Create(self, client_id):
		scenario = self.scenario_class(client_id)

		return scenario
