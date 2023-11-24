import time
import pybullet as pb
import numpy as np
import torch

import CONFIG
import observers.ObserverInterface as ObserverInterface

class BezierObserver(ObserverInterface.ObserverInterface):
	def __init__(self, client_id, episode_print_count, time_counter, episode_counter, episode_length, debug = False, is_saved = False):
		self.client_id = client_id
		self.time_counter = time_counter
		self.episode_counter = episode_counter
		self.is_saved = is_saved

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
		self.episode_length = episode_length
		self.episode_time_start = time.time()
		self.episode_print_count = episode_print_count

		self.distance_threshold = 0
		self.episode_length = 1
		self.progress_reward_decay = 20
		self.distance_reward_decay = 0.4#1.5

		self.debug = debug

	def RegisterEntities(self, scenario, drone, target, pole, floor):
		self.scenario = scenario
		self.drone = drone
		self.package = drone.GetPackageEntity()
		self.target = target
		self.pole = pole
		self.floor = floor

	def SaveData(self, state_path, value_path, max_path, flush_memory = False, file_type = ".pt"):
		if not self.is_saved:
			return

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

		if self.is_saved:
			control_points = torch.FloatTensor(self.drone.planner.control_points)

			state_indices = [0, episode_states.shape[0] // 2, -1]
			control_states = torch.FloatTensor(episode_states[state_indices])

			horizon_states = []

			for i in range(3):
				control_point = control_points[i]
				control_state = control_states[i]

				state = torch.cat((control_point, control_state))

				horizon_states.append(state)

			horizon_states = torch.stack(horizon_states)

			self.state_data.append(horizon_states)
			self.value_data.append(value)

		self.episode_states = []
		self.episode_data = []

	def Observe(self, timestep):

		drone_position = self.drone.GetPosition()
		target_position = self.target.GetPosition()

		target_offset = target_position - drone_position

		state_data = [
			self.drone.GetPosition(),
			self.drone.GetRotation(),
			self.drone.GetVelocity(),
			self.drone.GetAngularVelocity(),
		]

		distance = np.linalg.norm(target_offset)

		episode_data = {
			"collision": self.IsDroneCollision(),
			"dropped": self.drone.IsPackageDropped(),
			"distance": distance
		}

		state_data = np.concatenate(state_data)
		state_data = torch.FloatTensor(state_data)

		self.episode_states.append(state_data)
		self.episode_data.append(episode_data)

	def GetEpisodeValue(self, episode_data):

		is_collision = False
		is_dropped = False
		shortest_distance = 1e20
		distance_first = episode_data[0]["distance"]
		distance_last = episode_data[-1]["distance"]

		progress = distance_first - distance_last

		for i in range(len(episode_data)):
			data = episode_data[i]

			is_collision = is_collision or data["collision"]
			is_dropped = is_dropped or data["dropped"]
			distance = data["distance"]

			if distance < shortest_distance:
				shortest_distance = distance

		#collision_reward = 0
		#if is_collision:
		#	collision_reward = -1

		#progress_reward = progress * self.progress_reward_decay
		#progress_reward = self.SigmoidReward(progress)
		distance_reward = self.LinearReward(distance_last)
		#distance_reward = self.ExponentialReward(distance_last)

		reward = distance_reward# + collision_reward
		#reward = distance_reward + progress_reward
		#reward = progress_reward

		#if not is_dropped:
		#	reward = np.minimum(-0.5, collision_reward)

		episode_time_end = time.time() - self.episode_time_start
		self.avg_episode_time = (self.avg_episode_time + episode_time_end) / 2
		self.episode_time_start = time.time()

		if self.debug and self.client_id == 0 and self.episode_counter.GetCount() % self.episode_print_count == 0:

			print("============================")
			print("  Episode", self.episode_counter.GetCount() ,"- Client " + str(self.client_id))
			print("============================")
			#print("    Total Reward        :", reward)
			print("    Distance Reward     :", distance_reward)
			#print("    Progress Reward     :", progress_reward)
			#print("    Collision           :", is_collision)
			#print("    Dropped            :", is_dropped)
			print("")
			print("    Distance            :", "{:.2f}".format(distance_last))
			#print("    Progress            :", "{:.2f}".format(progress))
			print("    Average Episode Time:", "{:.2f}".format(self.avg_episode_time))

		if CONFIG.pause_every_episode and self.client_id == 0:
			print("\n[Simulation Paused]: Press enter to proceed.")
			input()

		return reward

	def LinearReward(self, distance):
		pseudo_distance = distance - self.distance_threshold
		pseudo_distance = pseudo_distance * self.distance_reward_decay
		pseudo_distance = 1 - np.maximum(0, pseudo_distance)
		#pseudo_distance = np.maximum(0, pseudo_distance)

		distance_reward = pseudo_distance

		return distance_reward

	def ExponentialReward(self, distance):
		pseudo_distance = distance - self.distance_threshold
		pseudo_distance = np.maximum(0, pseudo_distance)
		pseudo_distance = pseudo_distance * self.distance_reward_decay
		distance_reward = np.exp(-pseudo_distance)

		return distance_reward

	def SigmoidReward(self, progress):
		x = self.progress_reward_decay * progress
		x = 1 + np.exp(-x)
		x = 1 / x

		return x

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
