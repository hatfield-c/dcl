
import time
import math
import pybullet as pb
import numpy as np
import cv2

import scenarios.ScenarioInterface as ScenarioInterface
import scenarios.permuters.BoxPermuter as BoxPermuter
import scenarios.permuters.ListPermuter as ListPermuter
import scenarios.permuters.WaypointPermuter as WaypointPermuter

import physics.SimpleCounter as SimpleCounter
import render.RenderCamera as RenderCamera

import entities.agents.drones.DropDrone as DropDrone
import entities.drop_scenario.TargetPole as TargetPole
import entities.SimpleEntity as SimpleEntity

import planners.RandomDirectionPlanner as RandomDirectionPlanner
import planners.RandomRotorPlanner as RandomRotorPlanner
import planners.PidWaypointPlanner as PidWaypointPlanner
import planners.DiffusionPidPlanner as DiffusionPidPlanner
import planners.DiffusionRotorPlanner as DiffusionRotorPlanner

import controllers.PidForwardController as PidForwardController
import controllers.RotorController as RotorController
import controllers.DiffusionPidController as DiffusionPidController
import controllers.DiffusionRotorController as DiffusionRotorController

import events.EventQueue as EventQueue
import events.ChannelLogger as ChannelLogger

import observers.DropScenarioObserver as DropScenarioObserver
import observers.DistanceDiffusionObserver as DistanceDiffusionObserver

class DropScenario(ScenarioInterface.ScenarioInterface):
	def __init__(
			self,
			client_id,
			gravity_strength,
			max_episodes,
			simulation_episode_length,
			observer_episode_length,
			ai_type = "waypoint",
			state_data_path = None,
			max_data_path = None,
			value_data_path = None,
			episode_print_count = 1,
			render_scenario = True,
			save_render = False,
			is_saved = False
		):
		self.client_id = client_id
		self.ai_type = ai_type
		self.render_scenario = render_scenario
		self.save_render = save_render
		self.is_saved = is_saved

		self.max_episodes = max_episodes
		self.simulation_episode_length = simulation_episode_length
		self.observer_episode_length = observer_episode_length

		self.avg_episode_time = 0
		self.episode_time_start = time.time()

		self.time_counter = SimpleCounter.SimpleCounter(-1)
		self.episode_counter = SimpleCounter.SimpleCounter(-1)

		self.state_data_path = state_data_path
		self.max_data_path = max_data_path
		self.value_data_path = value_data_path

		pb.setGravity(0, 0, -gravity_strength)

		self.agents = {}
		self.dynamic_objects = {}
		self.static_objects = {}
		self.unified_entities = {}
		self.observers = {}

		self.event_queue = EventQueue.EventQueue()

		#self.scenario_observer = None
		#if state_data_path is not None:
			#self.scenario_observer = DropScenarioObserver.DropScenarioObserver(self.client_id, episode_print_count, self.time_counter, self.episode_counter, self.episode_length, True)
		self.scenario_observer = DistanceDiffusionObserver.DistanceDiffusionObserver(self.client_id, episode_print_count, self.time_counter, self.episode_counter, self.observer_episode_length, True, self.is_saved)

		self.observers["scenario_observer"] = self.scenario_observer

		self.camera = RenderCamera.RenderCamera(self.client_id, pitch = -20)

	def ResetScenario(self):

		#if self.scenario_observer is not None and not self.scenario_observer.IsEmpty():
		#	self.scenario_observer.EndEpisode()

		#self.time_counter.Reset()
		#self.episode_counter.Increment()

		#return

		for pb_id in self.unified_entities:
			entity = self.unified_entities[pb_id]
			permutation_data = entity.GetStatePermutation()

			entity.SetState(permutation_data)

		self.time_counter.Reset()
		self.episode_counter.Increment()

	def ResetObservers(self):
		if not self.scenario_observer.IsEmpty():
			self.scenario_observer.EndEpisode()

	def GetDroneAI(self, ai_type):
		planner = None
		controller = None

		if ai_type == "random_pid":
			planner = RandomDirectionPlanner.RandomDirectionPlanner(self.client_id, distance_scale = 2, debug = True)
			controller = PidForwardController.PidForwardController(force_scale = 1, torque_scale = 1)

		if ai_type == "random_rotor":
			planner = RandomRotorPlanner.RandomRotorPlanner(self.client_id)
			controller = RotorController.RotorController()

		if ai_type == "waypoint":
			waypoints = [np.array([0, -1, 6.5])]

			planner = PidWaypointPlanner.PidWaypointPlanner(self.client_id, waypoints, turn_strength = 1.5, time_counter = self.time_counter, debug = True)
			controller = PidForwardController.PidForwardController(force_scale = 1, torque_scale = 1)

		if ai_type == "diffusion_pid":
			waypoints = [np.array([0, -1, 6.5])]

			planner = DiffusionPidPlanner.DiffusionPidPlanner(self.client_id, self.time_counter, waypoints, turn_strength = 2, debug = True)
			controller = DiffusionPidController.DiffusionPidController(1, 1)

		if ai_type == "diffusion_rotor":
			planner = DiffusionRotorPlanner.DiffusionRotorPlanner(self.client_id, self.time_counter)
			controller = DiffusionRotorController.DiffusionRotorController(1, 1)

		return planner, controller

	def InstantiateDrone(self, start_pos, start_rotation, target):
		drone_urdf = "entity_files/drone_simple.urdf"

		planner, controller = self.GetDroneAI(self.ai_type)

		permuters = {
			"position": BoxPermuter.BoxPermuter(
				low_values = np.array([-5, -5, 0.4]),
				high_values = np.array([5, 5, 3])
			),
			"rotation": BoxPermuter.BoxPermuter(
				#low_values = np.array([-math.pi / 3, -math.pi / 3, 0]),
				#high_values = np.array([math.pi / 3, math.pi / 3, 2 * math.pi])
				low_values = np.array([-math.pi, -math.pi, -math.pi]),
				high_values = np.array([math.pi, math.pi, math.pi])
				#low_values = np.array([0, 0, 0]),
				#high_values = np.array([0, 0, 0])
			),
			"velocity": BoxPermuter.BoxPermuter(
				low_values = np.array([4, -4, -4]),
				high_values = np.array([4, 4, 4])
				#low_values = np.array([0, 0, 0]),
				#high_values = np.array([0, 0, 0])
			),
			"angular_velocity": BoxPermuter.BoxPermuter(
				low_values = np.array([-8, -8, -8]),
				high_values = np.array([8, 8, 8])
				#low_values = np.array([0, 0, 0]),
				#high_values = np.array([0, 0, 0])
			),
			"reset_package": ListPermuter.ListPermuter(choices_list = [ True ]),
			"start_position": ListPermuter.ListPermuter(choices_list = [ True ])
		}

		drone = DropDrone.DropDrone(
			urdf_name = drone_urdf,
			client_id = self.client_id,
			position = start_pos,
			rotation = start_rotation,
			planner = planner,
			controller = controller,
			permuters = permuters,
			target_entity = target
		)

		self.camera.SetTarget(drone)

		return drone

	def InstantiateEntities(self):

		pole = TargetPole.TargetPole(
			client_id = self.client_id,
			pole_urdf = None,#"entity_files/drop_scenario/target_pole.urdf",
			target_urdf = "entity_files/markers/blue_diamond.urdf",#"entity_files/drop_scenario/hoop_large.urdf",
			target_width = 0,#0.52,
			target_height = 0,#1.5,
			position = [0, 0, 1.5],
			is_static = True
		)

		start_pos = [0, -5, 2.5]
		start_rot = [0, 0, 0.785398 * 2]
		drone = self.InstantiateDrone(start_pos, start_rot, pole.target)

		self.agents["simple_drone"] = drone
		self.dynamic_objects[drone.GetPackageEntity().GetBulletId()] = drone.GetPackageEntity()
		self.static_objects["floor"] = SimpleEntity.SimpleEntity(
			urdf_name = "entity_files/20m_floor.urdf",
			client_id = self.client_id,
			is_static = True,
			texture_path = "entity_files/floor_material.png"
		)
		self.static_objects["pole"] = pole

		if self.scenario_observer is not None:
			self.scenario_observer.RegisterEntities(
				self,
				drone,
				pole.target,
				pole,
				self.static_objects["floor"]
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
			observer.Observe(self.time_counter.GetCount())

	def ProcessEvents(self):
		self.event_queue.ProcessQueue()

	def Render(self):
		if self.render_scenario:
			self.camera.FollowTarget()

		if self.save_render:

			target_position = self.agents["simple_drone"].GetCameraPosition()
			eye_position = np.array([
				target_position[0],
				target_position[1] - 1.3,
				target_position[2] + 0.5
			])
			up = np.array([0, 0, 1])

			view_matrix = pb.computeViewMatrix(eye_position, target_position, up)

			projection_matrix = pb.computeProjectionMatrixFOV(100, 1, 0.1, 12)

			result = pb.getCameraImage(
				width = 256,
				height = 256,
				viewMatrix = view_matrix,
				projectionMatrix = projection_matrix,
				shadow = 1,
				renderer = pb.ER_TINY_RENDERER,
				flags = pb.ER_NO_SEGMENTATION_MASK,
				physicsClientId = self.client_id,
			)

			rgb = result[2]
			rgb = rgb[:, :, [2, 1, 0]]
			episode_num = str(self.episode_counter.GetCount()).zfill(3)
			timestep = str(self.time_counter.GetCount()).zfill(4)

			filename = "data/render/frames/frame" + episode_num + "-" + timestep + ".png"

			cv2.imwrite(filename, rgb)

	def UpdateTime(self):
		self.time_counter.Increment()

		if self.scenario_observer is not None and self.episode_counter.GetCount() >= self.max_episodes:
			self.scenario_observer.SaveData(self.state_data_path, self.value_data_path, self.max_data_path)

			return False

		if self.time_counter.GetCount() % self.observer_episode_length == 0:
			self.ResetObservers()

		if self.time_counter.GetCount() == self.simulation_episode_length:
			self.ResetScenario()

		return True
