import pybullet as pb
import numpy as np
import torch

import observers.ObserverInterface as ObserverInterface

class DropScenarioObserver(ObserverInterface.ObserverInterface):
	def __init__(self, event_queue, channel_name):
		self.state_data = []
		self.value_data = []
		self.episode_states = []
		self.episode_data = []

		self.drone = None
		self.package = None
		self.target = None
		self.pole = None
		self.floor = None

		self.distance_threshold = 0
		self.episode_length = 1
		self.distance_reward_decay = 1

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

	def SaveData(self, state_path, value_path, flush_memory = False):
		state_data = torch.stack(self.state_data)
		value_data = torch.stack(self.value_data)

		torch.save(state_data, state_path)
		torch.save(value_data, value_path)

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

		isCollision = False
		isDropped = False
		shortest_distance = 1e20

		for i in range(len(episode_data)):
			data = episode_data[i]

			isCollision = isCollision or data["collision"]
			isDropped = isDropped or data["dropped"]
			distance = data["package_distance"]

			if distance < shortest_distance:
				shortest_distance = distance

		collision_reward = 0
		if isCollision:
			collision_reward = -1

		pseudo_distance = shortest_distance - self.distance_threshold
		pseudo_distance = np.maximum(0, pseudo_distance)
		pseudo_distance = -(pseudo_distance * self.distance_reward_decay)

		distance_reward = np.exp(pseudo_distance)

		reward = distance_reward + collision_reward

		if not isDropped:
			reward = np.minimum(0.5, reward)

		return reward

	def IsDroneCollision(self):
		target_collisions = pb.getContactPoints(self.drone.GetBulletId(), self.pole.GetBulletId())
		floor_collisions = pb.getContactPoints(self.drone.GetBulletId(), self.floor.GetBulletId())

		collisions = target_collisions + floor_collisions

		if len(collisions) == 0:
			return False

		return True

	def GetEpisodeCount(self):
		return len(self.state_data)
