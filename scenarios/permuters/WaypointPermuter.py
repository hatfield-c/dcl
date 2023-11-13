import numpy as np
import random

import scenarios.permuters.PermuterInterface as PermuterInterface

class WaypointPermuter(PermuterInterface.PermuterInterface):
	def __init__(self, num_points, origins, origin_weights, min_distance, max_distance, default_origin):
		self.num_points = num_points
		self.origins = origins
		self.origin_weights = origin_weights
		self.min_distance = min_distance
		self.max_distance = max_distance,
		self.default_origin = default_origin

	def GetPermutation(self, permutation_data = None):

		dice = random.random()
		total_weight = 0
		origin_index = 0
		for i in range(len(self.origins)):
			total_weight += self.origin_weights[i]

			if dice < total_weight:
				origin_index = i
				break

		start_position = self.origins[origin_index]
		waypoints = []
		for i in range(self.num_points):
			random_distance = np.random.uniform(self.min_distance, self.max_distance)
			random_direction = np.random.uniform(-1, 1, start_position.shape[0])

			waypoint = start_position + (random_distance * random_direction)
			waypoints.append(waypoint)

			start_position = waypoint

		default_origin = self.origins[self.default_origin]
		waypoints.append(default_origin)

		return waypoints
