
import math
import pybullet as pb
import numpy as np

import scenarios.ScenarioInterface as ScenarioInterface
import render.RenderCamera as RenderCamera

import entities.agents.drones.SimpleDrone as SimpleDrone
import entities.SimpleEntity as SimpleEntity

import controllers.PidForwardController as PidForwardController
import planners.PidWaypointPlanner as PidWaypointPlanner
import controllers.SimpleController as SimpleController
import planners.SimplePlanner as SimplePlanner

import events.EventQueue as EventQueue
import events.ChannelLogger as ChannelLogger
import observers.EntityObserver as EntityObserver

class WackADroneScenario(ScenarioInterface.ScenarioInterface):
	def __init__(self, pb_client):
		self.pb_client = pb_client
		self.time_step = 0

		pb.setGravity(0,0,-9.8)
		#pb.setGravity(0,0,0)

		self.agents = {}
		self.dynamic_objects = {}
		self.static_objects = {}
		self.observers = {}

		self.entity_logger = ChannelLogger.ChannelLogger("data/entity_data.txt", "entity_observer")

		self.event_queue = EventQueue.EventQueue()
		self.event_queue.RegisterConsumer(self.entity_logger)

		self.entity_observer = EntityObserver.EntityObserver(self.event_queue, "entity_observer")

		#self.observers["entity_observer"] = self.entity_observer
		self.camera = RenderCamera.RenderCamera(yaw = 150)

		self.unified_entities = {}

	def ResetScenario(self):
		for pb_id in self.unified_entities:
			entity = self.unified_entities[pb_id]

			state_data = {
				"position": entity.GetPosition(),
				"quaternion": entity.GetQuaternion(),
				"velocity": entity.GetVelocity(),
				"angular_velocity": entity.GetAngularVelocity()
			}

			entity.SetState(state_data)

	def InstantiateDrone(self, start_pos, start_rotation, waypoints):
		#drone_urdf = "entity_files/drone_simple.urdf"
		#drone_urdf = "entity_files/drone_debug.urdf"
		drone_urdf = "entity_files/drone_stick.urdf"

		planner = PidWaypointPlanner.PidWaypointPlanner(waypoints, turn_strength = 1.1)
		controller = PidForwardController.PidForwardController(force_scale = 1, torque_scale = 1)
		#planner = SimplePlanner.SimplePlanner()
		#controller = SimpleController.SimpleController()

		drone = SimpleDrone.SimpleDrone(
			urdf_name = drone_urdf,
			position = start_pos,
			rotation = start_rotation,
			planner = planner,
			controller = controller
		)

		return drone

	def InstantiateEntities(self):
		start_pos1 = [0, 0, 2.5]
		start_pos2 = [0, 20, 2.5]

		waypoints1 = [
			np.array(start_pos2)
		]
		waypoints2 = [
			np.array(start_pos1)
		]
		#start_rot = [-0.785398, 0, 0]
		start_rot1 = [-0.785398, 0, 0.785398 * 2]
		start_rot2 = [-0.785398, 0, -0.785398 * 2]
		drone1 = self.InstantiateDrone(start_pos1, start_rot1, waypoints1)
		drone2 = self.InstantiateDrone(start_pos2, start_rot2, waypoints2)

		self.agents["simple_drone1"] = drone1
		self.agents["simple_drone2"] = drone2

		self.camera.SetTarget(drone2)

		cube = SimpleEntity.SimpleEntity(urdf_name = "entity_files/debug_cube.urdf", position = [-2, 2, 3], rotation = [0.79, 0.79, 0])

		self.dynamic_objects["debug_cube"] = cube
		self.static_objects["floor"] = SimpleEntity.SimpleEntity(urdf_name = "entity_files/20m_floor.urdf", is_static = True)

		self.entity_observer.RegisterEntities([cube])

		for agent_id in self.agents:
			agent = self.agents[agent_id]

			self.unified_entities[agent.GetBulletId()] = agent

		for dynamic_obj_id in self.dynamic_objects:
			dynamic_object = self.dynamic_objects[dynamic_obj_id]

			self.unified_entities[dynamic_object.GetBulletId()] = dynamic_object

		for static_obj_id in self.static_objects:
			static_object = self.static_objects[static_obj_id]

			self.unified_entities[static_object.GetBulletId()] = static_object

	def UpdateEntities(self):

		for entity_id in self.unified_entities:
			entity = self.unified_entities[entity_id]

			entity.UpdateEntity()

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

	def Render(self):
		self.camera.FollowTarget()

	def UpdateTime(self):
		self.time_step = self.time_step + 1
