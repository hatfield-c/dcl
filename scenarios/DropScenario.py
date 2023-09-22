
import math
import pybullet as pb
import numpy as np

import scenarios.ScenarioInterface as ScenarioInterface
import scenarios.permuters.BoxPermuter as BoxPermuter
import scenarios.permuters.ListPermuter as ListPermuter
import render.RenderCamera as RenderCamera

import entities.agents.drones.DropDrone as DropDrone
import entities.StaticObject as StaticObject
import entities.DynamicObject as DynamicObject

import controllers.PidForwardController as PidForwardController
import planners.PidWaypointPlanner as PidWaypointPlanner
import controllers.SimpleController as SimpleController
import planners.SimplePlanner as SimplePlanner

import events.EventQueue as EventQueue
import events.ChannelLogger as ChannelLogger
import observers.EntityObserver as EntityObserver

class DropScenario(ScenarioInterface.ScenarioInterface):
	def __init__(self, pb_client):
		self.pb_client = pb_client
		self.time_step = 0

		pb.setGravity(0,0,-9.8)

		self.agents = {}
		self.dynamic_objects = {}
		self.static_objects = {}
		self.unified_entities = {}
		self.observers = {}

		self.entity_logger = ChannelLogger.ChannelLogger("data/entity_data.txt", "entity_observer")

		self.event_queue = EventQueue.EventQueue()
		self.event_queue.RegisterConsumer(self.entity_logger)

		self.entity_observer = EntityObserver.EntityObserver(self.event_queue, "entity_observer")

		#self.observers["entity_observer"] = self.entity_observer
		self.camera = RenderCamera.RenderCamera(yaw = 150)

	def ResetScenario(self):
		for pb_id in self.unified_entities:
			entity = self.unified_entities[pb_id]

			permutation_data = entity.GetStatePermutation()

			entity.SetState(permutation_data)

	def InstantiateDrone(self, start_pos, start_rotation):
		drone_urdf = "entity_files/drone_simple.urdf"

		waypoints = [
			np.array([0, 10, 1]),
			np.array([10, 4, 1]),
		]

		planner = PidWaypointPlanner.PidWaypointPlanner(waypoints, turn_strength = 1.1)
		controller = PidForwardController.PidForwardController(force_scale = 1, torque_scale = 1)

		drone = DropDrone.DropDrone(
			urdf_name = drone_urdf,
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
		#start_rot = [-0.785398, 0, 0]
		start_rot = [-0.785398, 0, 0.785398 * 2]
		drone = self.InstantiateDrone(start_pos, start_rot)

		self.agents["simple_drone"] = drone

		box_permuter = {
			"position": BoxPermuter.BoxPermuter(
				low_values = np.array([-2, -2, 4]),
				high_values = np.array([2, 2, 1])
			)
		}

		list_permuter = {
			"position": ListPermuter.ListPermuter(
				choices_list = [ np.array([-1, -1, 5]), np.array([1, -1, 5]), np.array([-1, 1, 5]) ]
			)
		}

		cube1 = DynamicObject.DynamicObject(
			urdf_name = "entity_files/debug_cube.urdf",
			position = [-2, 2, 3],
			rotation = [0.79, 0.79, 0],
			permuters = box_permuter
		)

		cube2 = DynamicObject.DynamicObject(
			urdf_name = "entity_files/debug_cube.urdf",
			position = [2, 2, 3],
			rotation = [0.79, 0.79, 0],
			permuters = list_permuter
		)

		self.dynamic_objects[cube1.GetBulletId()] = cube1
		self.dynamic_objects[cube2.GetBulletId()] = cube2
		self.static_objects["floor"] = StaticObject.StaticObject(urdf_name = "entity_files/20m_floor.urdf")

		self.entity_observer.RegisterEntities([cube1])

		for agent_id in self.agents:
			agent = self.agents[agent_id]

			self.unified_entities[agent.GetBulletId()] = agent

		for dynamic_obj_id in self.dynamic_objects:
			dynamic_object = self.dynamic_objects[dynamic_obj_id]

			self.unified_entities[dynamic_object.GetBulletId()] = dynamic_object

		for static_obj_id in self.static_objects:
			static_object = self.static_objects[static_obj_id]

			self.unified_entities[static_object.GetBulletId()] = static_object

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
