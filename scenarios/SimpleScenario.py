
import pybullet as pb

import scenarios.ScenarioInterface as ScenarioInterface

import entities.agents.drones.SimpleDrone as SimpleDrone
import entities.StaticObject as StaticObject
import entities.DynamicObject as DynamicObject

import actuators.SimpleDroneActuator as SimpleDroneActuator
import controllers.PidController as PidController
import planners.PidWaypointPlanner as PidWaypointPlanner
import controllers.SimpleController as SimpleController
import planners.SimplePlanner as SimplePlanner

import events.EventQueue as EventQueue
import events.ChannelLogger as ChannelLogger
import observers.EntityObserver as EntityObserver

class SimpleScenario(ScenarioInterface.ScenarioInterface):
	def __init__(
		self,
		pb_client
	):
		self.pb_client = pb_client
		self.time_step = 0
		
		pb.setGravity(0,0,-9.8)
		
		self.agents = {}
		self.dynamic_objects = {}
		self.static_objects = {}
		self.observers = {}
		
		self.entity_logger = ChannelLogger.ChannelLogger("data/entity_data.txt", "entity_observer")
		
		self.event_queue = EventQueue.EventQueue()
		self.event_queue.RegisterConsumer(self.entity_logger)
		
		self.entity_observer = EntityObserver.EntityObserver(self.event_queue, "entity_observer")
		
		self.observers["entity_observer"] = self.entity_observer
		
	def InstantiateDrone(self, start_pos):
		drone_urdf = "entity_files/drone_simple.urdf"
		
		actuator = SimpleDroneActuator.SimpleDroneActuator()
	
		#planner = PidWaypointPlanner.PidWaypointPlanner()	
		#controller = PidController.PidController()
		planner = SimplePlanner.SimplePlanner()	
		controller = SimpleController.SimpleController()
		
		drone = SimpleDrone.SimpleDrone(
			urdf_name = drone_urdf,
			position = start_pos,
			actuator = actuator,
			planner = planner,
			controller = controller
		)
		
		return drone
		
	def InstantiateEntities(self):
		
		start_pos = [0,0,1]
		drone = self.InstantiateDrone(start_pos)
		
		self.agents["simple_drone"] = drone
		
		cube = DynamicObject.DynamicObject(urdf_name = "entity_files/debug_cube.urdf", position = [-2, 2, 3], rotation = [0.79, 0.79, 0])
		 
		self.dynamic_objects["debug_cube"] = cube
		self.static_objects["floor"] = StaticObject.StaticObject(urdf_name = "entity_files/20m_floor.urdf")
		
		self.entity_observer.RegisterEntities([cube])
		
	def UpdateAgents(self):	
	
		for agent_id in self.agents:
			agent = self.agents[agent_id]
			
			agent.TakeAction()
	
	def UpdateObservers(self):
		for observer_name in self.observers:
			observer = self.observers[observer_name]
			observer.Observe(self.time_step)
	
	def ProcessEvents(self):
		self.event_queue.ProcessQueue()
		
	def UpdateTime(self):
		self.time_step = self.time_step + 1