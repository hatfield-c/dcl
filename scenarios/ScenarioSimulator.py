import pybullet as pb
import time

import CONFIG
import scenarios.SimpleScenario as SimpleScenario
import scenarios.WackADroneScenario as WackADroneScenario
import scenarios.DropScenario as DropScenario
import scenarios.UrbanNavigationScenario as UrbanNavigationScenario
import scenarios.TeleopScenario as TeleopScenario

class ScenarioSimulator:
	def __init__(self):
		pass

	def Run(self):

		client_ids = []
		scenarios = []

		for i in range(CONFIG.client_count):
			client_id = None

			if CONFIG.render_debug and i < 1:
				client_id = pb.connect(pb.GUI)
			else:
				client_id = pb.connect(pb.DIRECT)

			#scenario = SimpleScenario.SimpleScenario(client_id)
			#scenario = WackADroneScenario.WackADroneScenario(client_id)
			#scenario = UrbanNavigationScenario.UrbanNavigationScenario(client_id)
			#scenario = TeleopScenario.TeleopScenario(client_id)
			scenario = DropScenario.DropScenario(
				client_id = client_id,
				gravity_strength = CONFIG.gravity_strength,
				episode_count = CONFIG.episode_count,
				episode_length = CONFIG.episode_length,
				state_data_path = CONFIG.state_data_path,
				max_data_path = CONFIG.max_data_path,
				value_data_path = CONFIG.value_data_path
			)

			scenario.InstantiateEntities()
			scenario.ResetScenario()

			client_ids.append(client_id)
			scenarios.append(scenario)

		start_time = time.time()
		step = 0

		while True:

			is_simulating = True

			for i in range(CONFIG.client_count):
				client_id = client_ids[i]
				scenario = scenarios[i]

				scenario.Render()
				scenario.UpdateEntities()
				scenario.UpdateAgents()
				scenario.UpdateObservers()
				scenario.ProcessEvents()

				pb.stepSimulation(client_id)

				scenario_result = scenario.UpdateTime()

				is_simulating = is_simulating and scenario_result

			step += 1

			if not is_simulating:
				break

			time.sleep(CONFIG.timestep)

		for i in range(CONFIG.client_count):
			client_id = client_ids[i]

			pb.disconnect(client_id)

		end_time = time.time() - start_time

		print("\n\n==========================")
		print("Scenario complete!")
		print("    Run time:", "{:.2f}".format(end_time), "sec")
		print("==========================")
