import pybullet as pb
import time

import scenarios.SimpleScenario as SimpleScenario
import scenarios.DropScenario as DropScenario
import scenarios.TeleopScenario as TeleopScenario

class ScenarioSimulator:
	def __init__(self, scenario_factory):
		self.scenario_factory = scenario_factory

	def Run(self, client_count, render_scenario, timestep):

		client_ids = []
		scenarios = []

		for i in range(client_count):
			client_id = None

			if render_scenario and i < 1:
				client_id = pb.connect(pb.GUI)
			else:
				client_id = pb.connect(pb.DIRECT)

			scenario = self.scenario_factory.Create(client_id)

			scenario.InstantiateEntities()
			scenario.ResetScenario()

			client_ids.append(client_id)
			scenarios.append(scenario)

		start_time = time.time()
		step = 0

		while True:

			is_simulating = True

			for i in range(client_count):
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

			time.sleep(timestep)

		for i in range(client_count):
			client_id = client_ids[i]

			pb.disconnect(client_id)

		end_time = time.time() - start_time

		print("\n\n==========================")
		print("Scenario complete!")
		print("    Run time:", "{:.2f}".format(end_time), "sec")
		print("==========================")
