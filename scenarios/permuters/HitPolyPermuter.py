import numpy as np
import random
import math

import physics.Transform as Transform

import scenarios.permuters.PermuterInterface as PermuterInterface
import scenarios.permuters.BoxPermuter as BoxPermuter

class HitPolyPermuter(PermuterInterface.PermuterInterface):
	def __init__(self):
		self.directed_ratio = 0

	def GetPermutation(self, permutation_data = None):

		permutation = None
		dice_roll = random.random()

		if dice_roll < self.directed_ratio:
			permutation = self.GetDirectedPermutation()
		else:
			permutation = self.GetRandomPermutation()

		return permutation

	def GetConcavePosition(self, min_offset, max_offset, center):
		direction = np.random.uniform(
			[-1, -1, -1],
			[1, 1, 1]
		)
		direction = Transform.GetUnit(direction)

		offset = np.random.uniform(min_offset, max_offset)

		position = np.multiply(direction, offset) + center

		return position

	def GetRandomPermutation(self):
		permutation = {}

		#permutation["position"] = self.GetConcavePosition(
		#	min_offset = [1, 1, 0],
		#	max_offset = [5, 5, 1.6],
		#	center = [0, 0, 2]
		#)
		permutation["position"] = np.random.uniform(
			[-8, 0, 0.5],
			[8, 8, 8]
		)
		permutation["velocity"] = np.random.uniform(
			[-15, -15, -1],
			[15, 15, 1]
		)
		permutation["rotation"] = np.random.uniform(
			[-math.pi / 8, -math.pi / 8, 0],
			[math.pi / 8, math.pi / 8, 2 * math.pi]
		)
		permutation["angular_velocity"] = np.random.uniform(
			[-8, -8, -8],
			[8, 8, 8]
		)

		return permutation

	def GetDirectedPermutation(self):
		permutation = {}

		#position = self.GetConcavePosition(
		#	min_offset = [1, 1, 0],
		#	max_offset = [5, 5, 3],
		#	center = [0, 0, 2.5]
		#)

		position = np.random.uniform(
			[-3, -1, 0.5],
			[3, 8, 8]
		)

		pos_2d = -position[:2]
		direction = Transform.GetUnit(pos_2d)
		yaw = math.acos(direction[1])

		if pos_2d[0] > 0:
			yaw = -yaw

		rotation = np.array([-math.pi / 4, 0, yaw])

		max_speed = 10
		speed = np.random.uniform([0], [max_speed])
		#speed = np.random.uniform([5], [5])

		velocity = direction * speed

		velocity = np.array([velocity[0], velocity[1], 0])
		permutation["position"] = position
		permutation["rotation"] = rotation
		permutation["velocity"] = velocity
		permutation["angular_velocity"] = np.array([0, 0, 0])

		return permutation
