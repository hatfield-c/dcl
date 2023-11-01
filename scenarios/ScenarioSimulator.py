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

		client_id = None
		if CONFIG.render_count > 0:
			client_id = pb.connect(pb.GUI)
		else:
			client_id = pb.connect(pb.DIRECT)

		#scenario = SimpleScenario.SimpleScenario(client_id)
		#scenario = WackADroneScenario.WackADroneScenario(client_id)
		#scenario = UrbanNavigationScenario.UrbanNavigationScenario(client_id)
		#scenario = TeleopScenario.TeleopScenario(client_id)
		scenario = DropScenario.DropScenario(client_id)

		scenario.InstantiateEntities()

		start_time = time.time()
		step = 0

		while True:

			scenario.Render()
			scenario.UpdateEntities()
			scenario.UpdateAgents()
			scenario.UpdateObservers()
			scenario.ProcessEvents()

			pb.stepSimulation(client_id)

			step += 1

			isSimulating = scenario.UpdateTime()

			if not isSimulating:
				break


			time.sleep(CONFIG.timestep)

		pb.disconnect(client_id)

		end_time = time.time() - start_time

		print("==========================")
		print("\nScenario complete!")
		print("    Run time:", "{:.2f}".format(end_time), "sec")
		print("==========================")
