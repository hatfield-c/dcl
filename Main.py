import pybullet as pb
import time

import CONFIG
import scenarios.WackADroneScenario as WackADroneScenario

def Main():
	pb_client = pb.connect(pb.GUI)
	
	#scenario = SimpleScenario.SimpleScenario(pb_client)
	scenario = WackADroneScenario.WackADroneScenario(pb_client)
	scenario.InstantiateEntities()
	
	for i in range (10000):
		scenario.Render()
		scenario.UpdateAgents()
		scenario.UpdateObservers()
		scenario.ProcessEvents()
		
		pb.stepSimulation()
		
		scenario.UpdateTime()
		time.sleep(CONFIG.timestep)
		
	pb.disconnect()

Main()