import numpy as np

import planners.PlannerInterface as PlannerInterface

class PidWaypointPlanner(PlannerInterface.PlannerInterface):
	
	def __init__(self, waypoints, waypoint_threshold = 0.5):
		self.waypoints = waypoints
		self.waypoint_threshold = waypoint_threshold
		
		self.forward = np.array([0, 1, 0])
	
	def GetPlan(self, sensors, metadata):
		gps = sensors["gps"]
		gyro = sensors["gyro"]
		
		current_position = gps.ReadSensor(None)
		next_position = self.GetWaypoint(current_position)
		
		diff = next_position - current_position
		distance = np.linalg.norm(diff)
		
		if distance == 0:
			distance = 1
		
		desired_direction = diff / distance
		
		rotation = gyro.ReadSensor(None)
		forward_direction = self.RotationToDirection(rotation)
		
		current_state = { "direction": forward_direction, "distance": distance }
		next_state = { "direction":  desired_direction, "distance": 0}
		
		plan = [current_state, next_state]
		
		return plan
			
	def GetWaypoint(self, current_position):
		
		while(len(self.waypoints) > 0):
			next_position = self.waypoints[0]
			diff = next_position - current_position
			distance = np.linalg.norm(diff)
			
			if distance > self.waypoint_threshold:
				return next_position
			
			self.waypoints.pop(0)
				
		return current_position

	def RotationToDirection(self, rotation):
		x = np.cos(rotation[2]) * np.cos(rotation[0])
		y = np.sin(rotation[2]) * np.cos(rotation[0])
		z = np.sin(rotation[0])
		
		direction = np.array([x, y, z])
		magnitude = np.linalg.norm(direction)
		
		return direction / magnitude