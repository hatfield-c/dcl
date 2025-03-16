import time
import math
import pybullet as pb
import numpy as np
import torch

import CONFIG
import observers.ObserverInterface as ObserverInterface
import physics.Transform as Transform

class HitPolyObserver(ObserverInterface.ObserverInterface):
	def __init__(self, client_id, episode_print_count, time_counter, episode_counter, episode_length, debug = False, is_saved = False):
		self.client_id = client_id
		self.time_counter = time_counter
		self.episode_counter = episode_counter
		self.is_saved = is_saved

		self.state_data = []
		self.value_data = []
		self.episode_states = []
		self.episode_data = []
		self.is_episode_success = False

		self.drone = None
		self.package = None
		self.target = None
		self.pole = None
		self.floor = None

		self.avg_episode_time = 0
		self.episode_length = episode_length
		self.episode_time_start = time.time()
		self.episode_print_count = episode_print_count
		self.success_count = 0

		self.distance_threshold = 0
		self.episode_length = 1
		self.distance_reward_decay = 5

		self.debug = debug

	def RegisterEntities(self, scenario, drone, target, pole, floor):
		self.scenario = scenario
		self.drone = drone
		self.package = drone.GetPackageEntity()
		self.target = target
		self.pole = pole
		self.floor = floor

	def SaveData(self, state_path, max_path, value_path, flush_memory = False, file_type = ".pt"):
		if not self.is_saved:
			return

		state_data = torch.stack(self.state_data)
		value_data = torch.stack(self.value_data)

		max_data = torch.absolute(state_data)
		max_data = torch.max(max_data, dim = 1)
		max_data = max_data.values
		max_data = torch.max(max_data, dim = 0)
		max_data = max_data.values

		state_path = state_path + "-" + str(self.client_id) + "_" + str(CONFIG.app_index) + file_type
		max_path = max_path + "-" + str(self.client_id) + "_" + str(CONFIG.app_index) + file_type
		value_path = value_path + "-" + str(self.client_id) + "_" + str(CONFIG.app_index) + file_type

		if self.client_id == 0:
			print("App ", CONFIG.app_index, "- Saving at " + state_path)
			print("    State Data Shape:", state_data.shape)
			print("    Max Data Shape :", max_data.shape)
			print("    Value Data Shape:", value_data.shape)
			print("")

		torch.save(state_data, state_path)
		torch.save(max_data, max_path)
		torch.save(value_data, value_path)

		if flush_memory:
			self.state_data = []
			self.value_data = []
			self.episode_states = []
			self.episode_values = []

	def EndEpisode(self):

		if self.is_episode_success:
			self.success_count += 1

		episode_states = torch.stack(self.episode_states)
		value = self.GetEpisodeValue(self.episode_data)
		value = torch.FloatTensor([value])

		if self.is_saved:
			start_state = episode_states[0]

			self.state_data.append(start_state)
			self.value_data.append(value)

		self.episode_states = []
		self.episode_data = []
		self.is_episode_success = False

	def Observe(self, timestep):

		drone_position = self.drone.GetPosition()
		drone_rotation = self.drone.GetRotation()
		drone_quaternion = self.drone.GetQuaternion()
		drone_velocity = self.drone.GetVelocity()
		drone_angular_velocity = self.drone.GetAngularVelocity()

		package_position = self.drone.arm.package.GetPosition()
		target_position = self.target.GetPosition()

		xy_dist = np.linalg.norm(package_position[[0, 1]])

		is_success = False
		if xy_dist < 1.5 and package_position[2] > 0.5 and package_position[2] < 1:
			self.is_episode_success = True
			is_success = True

		target_offset = target_position - drone_position

		state_data = [
			#drone_position,
			#target_offset,
			drone_position,
			self.drone.GetRotation(),
			drone_velocity,
			self.drone.GetAngularVelocity(),
		]

		distance = np.linalg.norm(target_offset)

		episode_data = {
			"collision": self.IsDroneCollision(),
			"position": drone_position,
			"dropped": self.drone.IsPackageDropped(),
			"distance": distance,
			"velocity": drone_velocity,
			"angular_velocity": drone_angular_velocity,
			"rotation": drone_rotation,
			"target_offset": target_offset,
			"quaternion": drone_quaternion,
			"is_success": is_success
		}

		state_data = np.concatenate(state_data)
		state_data = torch.FloatTensor(state_data)

		self.episode_states.append(state_data)
		self.episode_data.append(episode_data)

	def GetEpisodeValue(self, episode_data):
		episode_time_end = time.time() - self.episode_time_start
		self.avg_episode_time = (self.avg_episode_time + episode_time_end) / 2
		self.episode_time_start = time.time()

		if self.debug and self.client_id == 0 and self.episode_counter.GetCount() % self.episode_print_count == 0:

			print("============================")
			print("  Episode", self.episode_counter.GetCount() ,"- App " + str(CONFIG.app_index))
			print("============================")
			print("    Is Success          :", self.is_episode_success)
			print("    Success Count       :", self.success_count)
			print("    Average Episode Time:", "{:.2f}".format(self.avg_episode_time))

		if CONFIG.pause_every_episode and self.client_id == 0:
			print("\n[Simulation Paused]: Press enter to proceed.")
			input()

		reward = 0
		if self.is_episode_success:
			reward = 1

		return reward

	def IsDroneCollision(self):
		pole_collisions = pb.getContactPoints(self.drone.GetBulletId(), self.pole.GetBulletId(), physicsClientId = self.client_id)
		hoop_collisions = pb.getContactPoints(self.drone.GetBulletId(), self.pole.target.GetBulletId(), physicsClientId = self.client_id)
		floor_collisions = pb.getContactPoints(self.drone.GetBulletId(), self.floor.GetBulletId(), physicsClientId = self.client_id)

		collisions = pole_collisions + hoop_collisions + floor_collisions

		if len(collisions) == 0:
			return False

		return True

	def IsEmpty(self):
		if len(self.episode_states) > 0:
			return False

		return True

	def GetEpisodeCount(self):
		return len(self.state_data)
