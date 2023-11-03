
import scenarios.DropScenario as DropScenario
import scenarios.factories.ScenarioFactoryInterface as ScenarioFactoryInterface

class DropScenarioFactory(ScenarioFactoryInterface.ScenarioFactoryInterface):
	def __init__(
		self,
		gravity_strength,
		episode_count,
		episode_length,
		ai_type,
		state_data_path,
		max_data_path,
		value_data_path,
	):
		self.gravity_strength = gravity_strength
		self.episode_count = episode_count
		self.episode_length = episode_length
		self.ai_type = ai_type
		self.state_data_path = state_data_path
		self.max_data_path = max_data_path
		self.value_data_path = value_data_path

	def Create(self, client_id):
		scenario = DropScenario.DropScenario(
			client_id = client_id,
			gravity_strength = self.gravity_strength,
			episode_count = self.episode_count,
			episode_length = self.episode_length,
			ai_type = self.ai_type,
			state_data_path = self.state_data_path,
			max_data_path = self.max_data_path,
			value_data_path = self.value_data_path,
			episode_print_count = 10
		)

		return scenario
