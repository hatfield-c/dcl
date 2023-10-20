import numpy as np

import scenarios.permuters.PermuterInterface as PermuterInterface

class WaypointPermuter(PermuterInterface.PermuterInterface):
	def __init__(self, num_points, min_distance, max_distance, noise_multiplier, noise_bias):
		self.num_points = num_points
		self.min_distance = min_distance
		self.max_distance = max_distance
		self.noise_multiplier = noise_multiplier
		self.noise_bias = noise_bias

	def GetPermutation(self, permutation_data = None):
		start_position = permutation_data["position"]

		random_distance = np.random.uniform(self.min_distance, self.max_distance)
		step_distances = np.linspace(0, random_distance, num = self.num_points)

		random_direction = np.random.rand(start_position.shape[0])
		random_direction = random_direction / (np.linalg.norm(random_direction) + 0.00001)

		noise_multiplier = np.random.triangular(0, self.noise_bias, self.noise_multiplier)

		waypoints = []
		for i in range(self.num_points):
			distance = step_distances[i]
			noise = np.random.rand(start_position.shape[0])

			waypoint = start_position + (random_direction * distance) + (noise * noise_multiplier)

			waypoints.append(waypoint)

		return waypoints
