
import scenarios.DropScenario as DropScenario
import scenarios.factories.ScenarioFactoryInterface as ScenarioFactoryInterface

class DropScenarioFactory(ScenarioFactoryInterface.ScenarioFactoryInterface):
	def __init__(
		self,
		gravity_strength,
		max_episodes,
		simulation_episode_length,
		observer_episode_length,
		ai_type,
		state_data_path,
		max_data_path,
		value_data_path,
		episode_print_count,
		render_scenario,
		save_render,
		is_saved
	):
		self.gravity_strength = gravity_strength
		self.max_episodes = max_episodes
		self.simulation_episode_length = simulation_episode_length
		self.observer_episode_length = observer_episode_length
		self.ai_type = ai_type
		self.state_data_path = state_data_path
		self.max_data_path = max_data_path
		self.value_data_path = value_data_path
		self.episode_print_count = episode_print_count
		self.render_scenario = render_scenario
		self.save_render = save_render
		self.is_saved = is_saved

	def Create(self, client_id, time_manager = None):

		scenario = DropScenario.DropScenario(
			client_id = client_id,
			gravity_strength = self.gravity_strength,
			max_episodes = self.max_episodes,
			simulation_episode_length = self.simulation_episode_length,
			observer_episode_length = self.observer_episode_length,
			ai_type = self.ai_type,
			state_data_path = self.state_data_path,
			max_data_path = self.max_data_path,
			value_data_path = self.value_data_path,
			episode_print_count = self.episode_print_count,
			render_scenario = self.render_scenario,
			save_render = self.save_render,
			is_saved = self.is_saved
		)

		return scenario
