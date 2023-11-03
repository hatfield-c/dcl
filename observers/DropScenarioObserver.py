import time
import pybullet as pb
import numpy as np
import torch

import observers.ObserverInterface as ObserverInterface

class DropScenarioObserver(ObserverInterface.ObserverInterface):
	def __init__(self, client_id, episode_print_count, event_queue, channel_name, debug = False):
		self.client_id = client_id

		self.state_data = []
		self.value_data = []
		self.episode_states = []
		self.episode_data = []

		self.drone = None
		self.package = None
		self.target = None
		self.pole = None
		self.floor = None

		self.avg_episode_time = 0
		self.episode_time_start = time.time()
		self.episode_count = 0
		self.episode_print_count = episode_print_count
		self.distance_threshold = 0
		self.episode_length = 1
		self.distance_reward_decay = 1

		self.debug = debug

	def RegisterEntities(self, scenario, drone, target, pole, floor, distance_threshold, episode_length, distance_reward_decay = 1):
		self.scenario = scenario
		self.drone = drone
		self.package = drone.GetPackageEntity()
		self.target = target
		self.pole = pole
		self.floor = floor

		self.distance_threshold = distance_threshold
		self.episode_length = episode_length
		self.distance_reward_decay = distance_reward_decay

	def SaveData(self, state_path, value_path, max_path, flush_memory = False, file_type = ".pt"):
		state_data = torch.stack(self.state_data)
		value_data = torch.stack(self.value_data)

		value_data = value_data.reshape(-1)

		if self.client_id == 0:
			print("\nClient ", self.client_id, "- Saving at " + state_path)

		max_data = torch.absolute(state_data)
		max_data = torch.max(max_data, dim = 1)
		max_data = max_data.values
		max_data = torch.max(max_data, dim = 0)
		max_data = max_data.values

		state_path = state_path + "-" + str(self.client_id) + file_type
		value_path = value_path + "-" + str(self.client_id) + file_type
		max_path = max_path + "-" + str(self.client_id) + file_type

		torch.save(state_data, state_path)
		torch.save(value_data, value_path)
		torch.save(max_data, max_path)

		if flush_memory:
			self.state_data = []
			self.value_data = []
			self.episode_states = []
			self.episode_values = []

	def EndEpisode(self):
		episode_states = torch.stack(self.episode_states)
		value = self.GetEpisodeValue(self.episode_data)
		value = torch.FloatTensor([value])

		self.state_data.append(episode_states)
		self.value_data.append(value)

		self.episode_states = []
		self.episode_data = []

		self.scenario.ResetScenario()
		self.episode_count += 1

	def Observe(self, timestep):

		drone_position = self.drone.GetPosition()
		target_position = self.target.GetPosition()
		package_position = self.package.GetPosition()

		target_offset = target_position - drone_position

		state_data = [
			self.drone.GetPreviousAction(),
			target_offset,
			self.drone.GetRotation(),
			self.drone.GetVelocity(),
			self.drone.GetAngularVelocity(),
		]

		package_distance = target_position - package_position
		package_distance = np.linalg.norm(package_distance)

		episode_data = {
			"collision": self.IsDroneCollision(),
			"dropped": self.drone.IsPackageDropped(),
			"package_distance": package_distance
		}

		state_data = np.concatenate(state_data)
		state_data = torch.FloatTensor(state_data)

		self.episode_states.append(state_data)
		self.episode_data.append(episode_data)

		if len(self.episode_states) == self.episode_length:
			self.EndEpisode()

	def GetEpisodeValue(self, episode_data):

		is_collision = False
		is_dropped = False
		shortest_distance = 1e20

		for i in range(len(episode_data)):
			data = episode_data[i]

			is_collision = is_collision or data["collision"]
			is_dropped = is_dropped or data["dropped"]
			distance = data["package_distance"]

			if distance < shortest_distance:
				shortest_distance = distance

		collision_reward = 0
		if is_collision:
			collision_reward = -1

		pseudo_distance = shortest_distance - self.distance_threshold
		pseudo_distance = np.maximum(0, pseudo_distance)
		pseudo_distance = -(pseudo_distance * self.distance_reward_decay)

		distance_reward = np.exp(pseudo_distance)

		reward = distance_reward + collision_reward

		if not is_dropped:
			reward = np.minimum(-0.5, collision_reward)

		episode_time_end = time.time() - self.episode_time_start
		self.avg_episode_time = (self.avg_episode_time + episode_time_end) / 2
		self.episode_time_start = time.time()

		if self.debug and self.client_id == 0 and self.episode_count % self.episode_print_count == 0:

			print("============================")
			print("  Episode", self.episode_count ,"- Client " + str(self.client_id))
			print("============================")
			print("    Reward              :", reward)
			print("    Collision           :", is_collision)
			print("    Dropped             :", is_dropped)
			print("    Distance            :", "{:.2f}".format(shortest_distance))
			print("    Average Episode Time:", "{:.2f}".format(self.avg_episode_time))

		return reward

	def IsDroneCollision(self):
		pole_collisions = pb.getContactPoints(self.drone.GetBulletId(), self.pole.GetBulletId(), physicsClientId = self.client_id)
		hoop_collisions = pb.getContactPoints(self.drone.GetBulletId(), self.pole.target.GetBulletId(), physicsClientId = self.client_id)
		floor_collisions = pb.getContactPoints(self.drone.GetBulletId(), self.floor.GetBulletId(), physicsClientId = self.client_id)

		collisions = pole_collisions + hoop_collisions + floor_collisions

		if len(collisions) == 0:
			return False

		return True

	def GetEpisodeCount(self):
		return len(self.state_data)
