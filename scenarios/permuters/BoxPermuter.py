import numpy as np

import scenarios.permuters.PermuterInterface as PermuterInterface

class BoxPermuter(PermuterInterface.PermuterInterface):
	def __init__(self, low_values, high_values):
		self.low_values = low_values
		self.high_values = high_values

	def GetPermutation(self, permutation_data = None):
		permutation = np.random.uniform(self.low_values, self.high_values)

		return permutation
