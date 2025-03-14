import numpy as np
import random
import math

import physics.Transform as Transform

import scenarios.permuters.PermuterInterface as PermuterInterface
import scenarios.permuters.BoxPermuter as BoxPermuter

class DemoPermuter(PermuterInterface.PermuterInterface):
	def __init__(self):
		pass

	def GetPermutation(self, permutation_data = None):
		permutation = self.GetRandomPermutation()

		return permutation

	def GetRandomPermutation(self):
		permutation = {}

		permutation["position"] = np.random.uniform(
			[-3, -8, 1.0],
			[3, -4, 1.5]
		)
		permutation["velocity"] = np.random.uniform(
			[-1, -1, -1],
			[1, 1, 1]
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

