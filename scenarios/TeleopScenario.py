import time
import math
import pybullet as pb
import numpy as np

import scenarios.ScenarioInterface as ScenarioInterface
import scenarios.permuters.BoxPermuter as BoxPermuter
import scenarios.permuters.ListPermuter as ListPermuter

import physics.SimpleCounter as SimpleCounter
import render.RenderCamera as RenderCamera

import entities.agents.drones.TeleopDrone as TeleopDrone
import entities.SimpleEntity as SimpleEntity

import planners.TeleopPlanner as TeleopPlanner
import planners.PidWaypointPlanner as PidWaypointPlanner
import controllers.PidForwardController as PidForwardController

import controllers.SimpleController as SimpleController
import planners.SimplePlanner as SimplePlanner

import events.EventQueue as EventQueue
import events.ChannelLogger as ChannelLogger
import observers.EntityObserver as EntityObserver

class TeleopScenario(ScenarioInterface.ScenarioInterface):
	def __init__(self, pb_client):
		self.pb_client = pb_client
		self.time_step = 0

		pb.setGravity(0,0,-9.8)

		self.agents = {}
		self.dynamic_objects = {}
		self.static_objects = {}
		self.unified_entities = {}
		self.observers = {}
		self.time_counter = SimpleCounter.SimpleCounter(0)

		self.entity_logger = ChannelLogger.ChannelLogger("data/entity_data.txt", "entity_observer")

		self.event_queue = EventQueue.EventQueue()
		self.event_queue.RegisterConsumer(self.entity_logger)

		self.entity_observer = EntityObserver.EntityObserver(self.event_queue, "entity_observer")

		#self.observers["entity_observer"] = self.entity_observer
		self.camera = RenderCamera.RenderCamera(self.pb_client, yaw = 150)

	def ResetScenario(self):
		for pb_id in self.unified_entities:
			entity = self.unified_entities[pb_id]

			permutation_data = entity.GetStatePermutation()

			entity.SetState(permutation_data)
			self.time_counter.Reset()

	def InstantiateDrone(self, start_pos, start_rotation):
		drone_urdf = "entity_files/drone_simple.urdf"

		waypoints = [
			np.array([0, 0, 0]),
			np.array([0, 0, 0]),
		]

		planner = TeleopPlanner.TeleopPlanner(self.pb_client, waypoints, turn_strength = 1.1, time_counter=self.time_counter)
		controller = PidForwardController.PidForwardController(force_scale = 1, torque_scale = 1)

		drone = TeleopDrone.TeleopDrone (
			urdf_name = drone_urdf,
			client_id = self.pb_client,
			position = start_pos,
			rotation = start_rotation,
			planner = planner,
			controller = controller,
			permuters = None
		)

		self.camera.SetTarget(drone)

		return drone

	def InstantiateEntities(self):

		start_pos = [0, 0, 2.5]
		start_rot = [0, 0, 0]
		drone = self.InstantiateDrone(start_pos, start_rot)

		self.agents["teleop_drone"] = drone
		self.static_objects["floor"] = SimpleEntity.SimpleEntity(urdf_name = "entity_files/20m_floor.urdf", client_id = self.pb_client, is_static = True)
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
			observer.Observe(self.time_counter.GetCount())

	def ProcessEvents(self):
		self.event_queue.ProcessQueue()

	def Render(self):
		self.camera.FollowTarget()

	def UpdateTime(self):
		self.time_counter.Increment()

		return True
