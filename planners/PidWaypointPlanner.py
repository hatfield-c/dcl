import numpy as np

import planners.PlannerInterface as PlannerInterface

class PidPWaypointlanner(PlannerInterface.PlannerInterface):
	
	def __init__(self, waypoints, waypoint_threshold = 1):
		self.waypoints = waypoints
		self.waypoint_threshold
		
		self.forward = np.array([0, 1, 0])
	
	def GetPlan(self, sensors, metadata):
		gps = sensors["gps"]
		quat = sensors["quat"]
		
		current_position = gps.ReadSensor()
		next_position = self.GetWaypoint(current_position)
		
		diff = next_position - current_position
		distance = np.linalg.norm(diff)
		
		if distance == 0:
			distance = 1
		
		desired_direction = diff / distance
		
		quaternion = quat.ReadSensor()
		forward_direction = quaternion * self.forward
		
		current_state = { "direction": forward_direction, "distance": distance }
		next_state = { "direction":  desired_direction, "distance": 0}
		
		plan = [current_state, next_state]
			
	def GetWaypoint(self, current_position):
		
		while(len(self.waypoints) > 0):
			next_position = self.waypoints[0]
			diff = next_position - current_position
			distance = np.linalg.norm(diff)
			
			if distance > self.waypoint_threshold:
				return next_position
			
			self.waypoints.pop(0)
				
		return current_position
