
import time
import math
import pybullet as pb
import numpy as np
import cv2

import scenarios.ScenarioInterface as ScenarioInterface
import scenarios.permuters.BoxPermuter as BoxPermuter
import scenarios.permuters.ListPermuter as ListPermuter
import scenarios.permuters.WaypointPermuter as WaypointPermuter
import scenarios.permuters.HitPolyPermuter as HitPolyPermuter

import physics.SimpleCounter as SimpleCounter
import render.RenderCamera as RenderCamera

import entities.agents.drones.DropDrone as DropDrone
import entities.drop_scenario.TargetPole as TargetPole
import entities.SimpleEntity as SimpleEntity

import planners.DiffusionBezierAlignmentPlanner as DiffusionBezierAlignmentPlanner
import planners.PidAlignmentPlanner as PidAlignmentPlanner
import planners.ImmediateReleasePlanner as ImmediateReleasePlanner
import planners.HitPolyPlanner as HitPolyPlanner

import controllers.PidForwardController as PidForwardController

import events.EventQueue as EventQueue
import events.ChannelLogger as ChannelLogger

import observers.HitPolyObserver as HitPolyObserver

class HitPolyScenario(ScenarioInterface.ScenarioInterface):
	def __init__(
			self,
			client_id,
			gravity_strength,
			max_episodes,
			episode_length,
			ai_type,
			render_poly = False,
			state_data_path = None,
			max_data_path = None,
			value_data_path = None,
			episode_print_count = 1,
			render_scenario = True,
			save_render = False,
			save_data = False,
			is_logged = False
		):
		self.client_id = client_id
		self.ai_type = ai_type
		self.render_poly = render_poly
		self.render_scenario = render_scenario
		self.save_render = save_render
		self.save_data = save_data
		self.is_logged = is_logged

		if self.is_logged:
			self.logId = pb.startStateLogging(pb.STATE_LOGGING_PROFILE_TIMINGS, "./timings.json", physicsClientId = self.client_id)

		if client_id != 0:
			self.render_scenario = False

		self.max_episodes = max_episodes
		self.episode_length = episode_length

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

		self.scenario_observer = HitPolyObserver.HitPolyObserver(self.client_id, episode_print_count, self.time_counter, self.episode_counter, self.episode_length, True, self.save_data)

		self.observers["scenario_observer"] = self.scenario_observer

		self.camera = RenderCamera.RenderCamera(self.client_id, pitch = -20, yaw = 0)

	def ResetScenario(self):
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

		if ai_type == "pid_align_data":
			release_planner = ImmediateReleasePlanner.ImmediateReleasePlanner()
			planner = PidAlignmentPlanner.PidAlignmentPlanner(self.client_id, episode_length = self.episode_length, release_planner = release_planner, debug = True)
			controller = PidForwardController.PidForwardController(force_scale = 1, torque_scale = 1)

		if ai_type == "pid_align_poly":
			release_planner = HitPolyPlanner.HitPolyPlanner(self.client_id, self.render_poly)
			planner = PidAlignmentPlanner.PidAlignmentPlanner(self.client_id, episode_length = self.episode_length, release_planner = release_planner, debug = True)
			controller = PidForwardController.PidForwardController(force_scale = 1, torque_scale = 1)

		return planner, controller

	def GetDronePermuters(self, ai_type, planner, controller):
		permuters = {}

		if ai_type == "pid_align_data" or ai_type == "pid_align_poly":
			permuters["hit_poly"] = HitPolyPermuter.HitPolyPermuter()
			permuters["reset_package"] = ListPermuter.ListPermuter(choices_list = [ True ])

		return permuters


	def InstantiateDrone(self, start_pos, start_rotation, target):
		drone_urdf = "entity_files/drone_simple.urdf"

		planner, controller = self.GetDroneAI(self.ai_type)
		permuters = self.GetDronePermuters(self.ai_type, planner, controller)

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
			pole_urdf = "entity_files/drop_scenario/target_pole.urdf",
			target_urdf = "entity_files/drop_scenario/hoop_large.urdf",
			target_width = 0.52,
			target_height = 2,
			position = [-0.55, 0, -.7],
			is_static = True
		)

		start_pos = [0, 0, 2.5]
		start_rot = [0, 0, 0.785398 * 2]
		drone = self.InstantiateDrone(start_pos, start_rot, pole.target)

		#self.static_objects["alignment_visualizer"] = SimpleEntity.SimpleEntity(
		#	urdf_name = "entity_files/drop_scenario/alignment_line.urdf",
		#	client_id = self.client_id,
		#	is_static = True,
		#	position = [0, 0, 2.5]
		#)

		self.agents["simple_drone"] = drone
		self.dynamic_objects[drone.GetPackageEntity().GetBulletId()] = drone.GetPackageEntity()
		self.static_objects["floor"] = SimpleEntity.SimpleEntity(
			urdf_name = "entity_files/20m_floor.urdf",
			client_id = self.client_id,
			is_static = True,
			texture_path = "entity_files/floor_material.png",
			position = [0, 10, 0]
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

			agent.ApplyDrag()
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
			lens_distance = 1.3

			marker_position = np.array([0, 100, 1.5])#self.static_objects["pole"].target.GetPosition()
			drone_position = self.agents["simple_drone"].GetCameraPosition()
			rotation = self.agents["simple_drone"].GetRotation()

			offset_direction = drone_position - marker_position
			offset_magnitude = np.linalg.norm(offset_direction)

			if offset_magnitude == 0:
				offset_magnitude = 1

			offset_direction = offset_direction / offset_magnitude
			offset_direction = offset_direction[:2] * lens_distance

			#x_offset = math.cos(-math.pi / 2) * lens_distance
			#y_offset = math.sin(-math.pi / 2) * lens_distance

			x_offset = offset_direction[0]
			y_offset = offset_direction[1]

			eye_position = np.array([
				drone_position[0] + x_offset,
				drone_position[1] + y_offset,# - 1.3,
				drone_position[2] + 0.5
			])
			up = np.array([0, 0, 1])

			view_matrix = pb.computeViewMatrix(eye_position, drone_position, up)

			projection_matrix = pb.computeProjectionMatrixFOV(100, 1, 0.1, 30)

			result = pb.getCameraImage(
				width = 512,#256,
				height = 512,#256,
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
			if self.save_data:
				self.scenario_observer.SaveData(self.state_data_path, self.max_data_path, self.value_data_path)

			if self.is_logged:
				pb.stopStateLogging(self.logId)

			return False

		if self.time_counter.GetCount() % self.episode_length == 0:
			self.ResetObservers()
			self.ResetScenario()

		return True
