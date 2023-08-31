
import pybullet as pb

import scenarios.ScenarioInterface as ScenarioInterface
import entities.agents.drones.SimpleDrone as SimpleDrone
import entities.StaticObject as StaticObject
import entities.DynamicObject as DynamicObject
import events.EventQueue as EventQueue
import events.ChannelLogger as ChannelLogger

class SimpleScenario(ScenarioInterface.ScenarioInterface):
	def __init__(
		self,
		pb_client
	):
		self.pb_client = pb_client
		
		pb.setGravity(0,0,-9.8)
		
		self.agents = {}
		self.dynamic_objects = {}
		self.static_objects = {}
		
		self.time_channel_logger = ChannelLogger.ChannelLogger("data/out.txt", "simple_time")
		self.event_queue = EventQueue.EventQueue()
		self.event_queue.RegisterConsumer(self.time_channel_logger)
		
	def InstantiateEntities(self):
		
		startPos = [0,0,1]
		drone_urdf = "entity_files/drone_simple.urdf"
		drone = SimpleDrone.SimpleDrone(
			urdf_name = drone_urdf,
			position = startPos
		)
		
		self.agents["simple_drone"] = drone
		
		self.dynamic_objects["debug_cube"] = DynamicObject.DynamicObject(urdf_name = "entity_files/debug_cube.urdf", position = [-2, 2, 3], rotation = [0.79, 0.79, 0])
		self.static_objects["floor"] = StaticObject.StaticObject(urdf_name = "entity_files/20m_floor.urdf")
		
	def UpdateAgents(self):	
	
		for agent_id in self.agents:
			agent = self.agents[agent_id]
			
			agent.TakeAction()
	
	def ProcessEvents(self):
		self.event_queue.ProcessQueue()