import random

import scenarios.permuters.PermuterInterface as PermuterInterface

class ListPermuter(PermuterInterface.PermuterInterface):
	def __init__(self, choices_list):
		self.choices_list = choices_list

	def GetPermutation(self, permutation_data = None):
		index = random.randrange(0, len(self.choices_list))
		permutation = self.choices_list[index]

		return permutation
