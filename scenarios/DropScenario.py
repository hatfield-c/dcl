
import math
import pybullet as pb
import numpy as np

import scenarios.ScenarioInterface as ScenarioInterface
import scenarios.permuters.BoxPermuter as BoxPermuter
import scenarios.permuters.ListPermuter as ListPermuter
import scenarios.permuters.WaypointPermuter as WaypointPermuter
import render.RenderCamera as RenderCamera

import entities.agents.drones.DropDrone as DropDrone
import entities.drop_scenario.TargetPole as TargetPole
import entities.SimpleEntity as SimpleEntity

import controllers.PidForwardController as PidForwardController
import planners.PidWaypointPlanner as PidWaypointPlanner

import events.EventQueue as EventQueue
import observers.DropScenarioObserver as DropScenarioObserver

class DropScenario(ScenarioInterface.ScenarioInterface):
	def __init__(self, pb_client):
		self.pb_client = pb_client
		self.time_step = 0
		self.event_distance_range = 7

		self.episode_count = 10
		self.episode_length = 10

		self.state_data_path = "data/state_data.pt"
		self.max_data_path = "data/max_data.pt"
		self.value_data_path = "data/value_data.pt"

		pb.setGravity(0,0,-9.8)

		self.agents = {}
		self.dynamic_objects = {}
		self.static_objects = {}
		self.unified_entities = {}
		self.observers = {}

		self.event_queue = EventQueue.EventQueue()

		self.scenario_observer = DropScenarioObserver.DropScenarioObserver(None, None)
		#self.observers["scenario_observer"] = self.scenario_observer

		self.camera = RenderCamera.RenderCamera(yaw = 150)

	def ResetScenario(self):
		for pb_id in self.unified_entities:
			entity = self.unified_entities[pb_id]
			permutation_data = entity.GetStatePermutation()

			entity.SetState(permutation_data)

		self.time_step = 0

	def InstantiateDrone(self, start_pos, start_rotation):
		drone_urdf = "entity_files/drone_simple.urdf"

		waypoints = [
			np.array([0, -10, 2.5]),
			np.array([10, 4, 3]),
		]

		planner = PidWaypointPlanner.PidWaypointPlanner(waypoints, turn_strength = 1.1)
		controller = PidForwardController.PidForwardController(force_scale = 1, torque_scale = 1)

		permuters = {
			# "position_place_holder": "drone position permuter must be placed before waypoint permuter",
			"waypoint": WaypointPermuter.WaypointPermuter(
				num_points = 10,
				min_distance = 3,
				max_distance = 10,
				noise_multiplier = 2,
				noise_bias = 0.6
			)
		}

		drone = DropDrone.DropDrone(
			urdf_name = drone_urdf,
			position = start_pos,
			rotation = start_rotation,
			planner = planner,
			controller = controller,
			permuters = permuters
		)

		self.camera.SetTarget(drone)

		return drone

	def InstantiateEntities(self):

		start_pos = [0, 6.5, 2.5]
		start_rot = [0, 0, 0.785398 * 4]
		drone = self.InstantiateDrone(start_pos, start_rot)

		self.agents["simple_drone"] = drone

		box_permuter = {
			"position": BoxPermuter.BoxPermuter(
				low_values = np.array([-5, -2, 4]),
				high_values = np.array([-5, -2, 1])
			)
		}

		list_permuter = {
			"position": ListPermuter.ListPermuter(
				choices_list = [ np.array([-9, -1, 5]), np.array([8, -1, 5]), np.array([-7, 1, 5]) ]
			)
		}

		cube1 = SimpleEntity.SimpleEntity(
			urdf_name = "entity_files/debug_cube.urdf",
			position = [-2, 2, 3],
			rotation = [0.79, 0.79, 0],
			permuters = box_permuter
		)

		cube2 = SimpleEntity.SimpleEntity(
			urdf_name = "entity_files/debug_cube.urdf",
			position = [2, 2, 3],
			rotation = [0.79, 0.79, 0],
			permuters = list_permuter
		)

		target = SimpleEntity.SimpleEntity(
			urdf_name = "entity_files/markers/green_diamond.urdf",
			position = [5, 5, 0],
			rotation = [0, 0, 0]
		)

		pole = TargetPole.TargetPole(
			pole_urdf = "entity_files/drop_scenario/target_pole.urdf",
			target_urdf = "entity_files/drop_scenario/hoop_large.urdf",
			target_width = 0.52,
			target_height = 1.5,
			position = [-0.2, -3 ,0],
			is_static = True
		)

		self.dynamic_objects[cube1.GetBulletId()] = cube1
		self.dynamic_objects[cube2.GetBulletId()] = cube2
		self.dynamic_objects[drone.GetPackageEntity().GetBulletId()] = drone.GetPackageEntity()
		self.static_objects["floor"] = SimpleEntity.SimpleEntity(urdf_name = "entity_files/20m_floor.urdf", is_static = True)
		self.static_objects["target"] = target
		self.static_objects["pole"] = pole

		self.scenario_observer.RegisterEntities(
			self,
			drone,
			target,
			pole,
			self.static_objects["floor"],
			distance_threshold = 1,
			episode_length = self.episode_length,
			distance_reward_decay = 1
		)

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

		if self.scenario_observer.GetEpisodeCount() >= self.episode_count:
			self.scenario_observer.SaveData(self.state_data_path, self.value_data_path, self.max_data_path)

			return False

		return True
