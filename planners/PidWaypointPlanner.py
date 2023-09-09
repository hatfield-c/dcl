import numpy as np
import math

import planners.PlannerInterface as PlannerInterface

class PidWaypointPlanner(PlannerInterface.PlannerInterface):
	
	def __init__(self, waypoints, waypoint_threshold = 0.5):
		self.waypoints = waypoints
		self.waypoint_threshold = waypoint_threshold
		
		self.forward = np.array([0, 1, 0])
	
	def GetPlan(self, sensors, metadata):
		gps = sensors["gps"]
		quat = sensors["quat"]
		velocity_sensor = sensors["velocity"]
		
		current_position = gps.ReadSensor(None)
		next_position = self.GetWaypoint(current_position)
		
		diff = next_position - current_position
		distance = np.linalg.norm(diff)
		
		if distance == 0:
			distance = 1
		
		desired_direction = diff / distance
		
		velocity = velocity_sensor.ReadSensor(None)

		current_quat = quat.ReadSensor(None)

		plan = {
			"current_quat": current_quat,
			"current_altitude": current_position[2],
			"desired_direction": desired_direction, 
			"desired_altitude": next_position[2],
			"velocity": velocity
		}
		
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