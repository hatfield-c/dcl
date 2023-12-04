
import scenarios.HitPolyScenario as HitPolyScenario
import scenarios.factories.ScenarioFactoryInterface as ScenarioFactoryInterface

class HitPolyScenarioFactory(ScenarioFactoryInterface.ScenarioFactoryInterface):
	def __init__(
		self,
		gravity_strength,
		max_episodes,
		episode_length,
		ai_type,
		render_poly,
		state_data_path,
		value_data_path,
		max_data_path,
		episode_print_count,
		render_scenario,
		save_render,
		save_data
	):
		self.gravity_strength = gravity_strength
		self.max_episodes = max_episodes
		self.episode_length = episode_length
		self.ai_type = ai_type
		self.render_poly = render_poly
		self.state_data_path = state_data_path
		self.value_data_path = value_data_path
		self.max_data_path = max_data_path
		self.episode_print_count = episode_print_count
		self.render_scenario = render_scenario
		self.save_render = save_render
		self.save_data = save_data

	def Create(self, client_id, time_manager = None):

		scenario = HitPolyScenario.HitPolyScenario(
			client_id = client_id,
			gravity_strength = self.gravity_strength,
			max_episodes = self.max_episodes,
			episode_length = self.episode_length,
			ai_type = self.ai_type,
			render_poly = self.render_poly,
			state_data_path = self.state_data_path,
			max_data_path = self.max_data_path,
			value_data_path = self.value_data_path,
			episode_print_count = self.episode_print_count,
			render_scenario = self.render_scenario,
			save_render = self.save_render,
			save_data = self.save_data
		)

		return scenario
