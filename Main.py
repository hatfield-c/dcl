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
	scenario = TeleopScenario.TeleopScenario(pb_client)
	scenario.InstantiateEntities()

	for i in range (10000):
		scenario.Render()
		scenario.UpdateEntities()
		scenario.UpdateAgents()
		scenario.UpdateObservers()
		scenario.ProcessEvents()

		pb.stepSimulation()

		if i % 300 == 0:
			print("reset!")
			scenario.ResetScenario()

		scenario.UpdateTime()
		time.sleep(CONFIG.timestep)

	pb.disconnect()

Main()
