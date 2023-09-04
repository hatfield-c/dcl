import pybullet as pb
import time

import CONFIG
import scenarios.SimpleScenario as SimpleScenario

def Main():
	pb_client = pb.connect(pb.GUI)
	
	scenario = SimpleScenario.SimpleScenario(pb_client)
	scenario.InstantiateEntities()
	
	for i in range (10000):
		scenario.UpdateAgents()
		scenario.UpdateObservers()
		scenario.ProcessEvents()
		
		pb.stepSimulation()
		
		scenario.UpdateTime()
		time.sleep(CONFIG.timestep)
		
	pb.disconnect()

Main()