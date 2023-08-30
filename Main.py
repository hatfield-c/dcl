import pybullet as pb
import time
import pybullet_data

import scenarios.SimpleScenario as SimpleScenario

def Main():
	pb_client = pb.connect(pb.GUI)
	
	scenario = SimpleScenario.SimpleScenario(pb_client)
	scenario.InstantiateEntities()
	
	for i in range (10000):
		if i % 100 == 0:
			scenario.event_queue.AddEvent("simple_time", "[Simulation Step: " + str(i) + "]")
		
		scenario.UpdateAgents()
		scenario.ProcessEvents()
		
		pb.stepSimulation()
		
		time.sleep(1./240.)
		
	pb.disconnect()

Main()