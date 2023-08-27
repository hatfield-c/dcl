import pybullet as pb
import time
import pybullet_data

import SimpleScenario

def Main():
	pb_client = pb.connect(pb.GUI)
	
	scenario = SimpleScenario.SimpleScenario(pb_client)
	scenario.InstantiateEntities()
	
	for i in range (10000):
		scenario.UpdateAgents()
		pb.stepSimulation()
		time.sleep(1./240.)
		
	pb.disconnect()

Main()