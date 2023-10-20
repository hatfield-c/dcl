import numpy as np
import math

import physics.Transform as Transform
import planners.PlannerInterface as PlannerInterface
import planners.PidWaypointPlanner as PidWaypointPlanner

class RandomLinearPlanner(PlannerInterface.PlannerInterface):

	def __init__(self, num_points, min_distance, max_distance):
		self.num_points = num_points
		self.min_distance = min_distance
		self.max_distance = max_distance

		self.waypoint_planner = None

	def GetPlan(self, sensors, metadata):

		plan = self.waypoint_planner.GetPlan(sensors, metadata)

		return plan

	def GenerateNewPath(self, sensors, metadata):
		telemetry = sensors["telemetry"]
		sensor_data = telemetry.ReadSensor(None)

		random_distance = np.uniform(self.min_distance, self.max_distance)
		step_distances = np.linspace(0, self.random_distance, num = self.num_points)

		start_position = sensor_data["position"]

		random_direction = np.random.rand(start_position.shape)
		random_direction = random_direction / (np.linalg.norm + 0.00001)

		waypoints = []

		self.waypoint_planner = PidWaypointPlanner.PidWaypointPlanner(
			waypoints = waypoints,
			waypoint_threshold = 0.1,
			turn_strength = 1.1
		)
