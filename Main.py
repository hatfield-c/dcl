import pybullet as pb
import time

import CONFIG
import scenarios.SimpleScenario as SimpleScenario
import scenarios.WackADroneScenario as WackADroneScenario
import scenarios.DropScenario as DropScenario
import scenarios.UrbanNavigationScenario as UrbanNavigationScenario
import scenarios.TeleopScenario as TeleopScenario

def Main():
	pb_client = pb.connect(pb.GUI)

	#scenario = SimpleScenario.SimpleScenario(pb_client)
	#scenario = WackADroneScenario.WackADroneScenario(pb_client)
	#scenario = UrbanNavigationScenario.UrbanNavigationScenario(pb_client)
	#scenario = TeleopScenario.TeleopScenario(pb_client)
	scenario = DropScenario.DropScenario(pb_client)

	scenario.InstantiateEntities()

	start_time = time.time()

	while True:
		scenario.Render()
		scenario.UpdateEntities()
		scenario.UpdateAgents()
		scenario.UpdateObservers()
		scenario.ProcessEvents()

		pb.stepSimulation()

		isSimulating = scenario.UpdateTime()

		if not isSimulating:
			break

		time.sleep(CONFIG.timestep)

	pb.disconnect()

	end_time = time.time() - start_time

	print("==========================")
	print("\nScenario complete!")
	print("    Run time:", "{:.2f}".format(end_time), "sec")
	print("==========================")

Main()
