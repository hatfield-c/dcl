
import scenarios.DroneMazeScenario as DroneMazeScenario
import scenarios.factories.ScenarioFactoryInterface as ScenarioFactoryInterface

class DroneMazeScenarioFactory(ScenarioFactoryInterface.ScenarioFactoryInterface):
	def __init__(
		self,
		gravity_strength,
		max_episodes,
		episode_length,
	):
		self.gravity_strength = gravity_strength
		self.max_episodes = max_episodes
		self.episode_length = episode_length

	def Create(self, client_id, time_manager = None):

		scenario = DroneMazeScenario.DroneMazeScenario(
			client_id = client_id,
			gravity_strength = self.gravity_strength,
			max_episodes = self.max_episodes,
			episode_length = self.episode_length,
		)

		return scenario
