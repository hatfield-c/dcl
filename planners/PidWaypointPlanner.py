import numpy as np
import math

import physics.Transform as Transform
import planners.PlannerInterface as PlannerInterface

class PidWaypointPlanner(PlannerInterface.PlannerInterface):
	
	def __init__(self, waypoints, waypoint_threshold = 0.5, turn_strength = 1):
		self.waypoints = waypoints
		self.waypoint_threshold = waypoint_threshold
		self.turn_strength = turn_strength
		
		self.current_action = "move"
	
	def GetPlan(self, sensors, metadata):
		telem = sensors["telem"]
		
		sensorCall = telem.ReadSensor(None)
		
		current_position = sensorCall["gps"]
		next_position = self.GetWaypoint(current_position)
		
		diff = next_position - current_position
		distance = np.linalg.norm(diff)
		
		if distance == 0:
			distance = 1
		
		waypoint_direction = diff / distance

		velocity = sensorCall["velocity"]
		current_quat = sensorCall["quat"]

		desired_direction = self.GetDesiredForwardDirection(waypoint_direction, velocity)

		plan = {
			"action": self.current_action,
			"current_quat": current_quat,
			"current_altitude": current_position[2],
			"desired_direction": desired_direction, 
			"desired_altitude": next_position[2],
			"velocity": velocity
		}
		
		return plan
			
	def GetDesiredForwardDirection(self, target_direction, velocity):
		velocity_xy = velocity[[0, 1]]
		target_xy = target_direction[[0, 1]]
		
		speed = np.linalg.norm(velocity_xy)
		
		if speed == 0:
			velocity_xy = target_xy
			speed = 1
			
		velocity_xy = velocity_xy / speed
		
		vel_to_target = target_xy - velocity_xy
		new_direction = target_xy + (vel_to_target * self.turn_strength)
		new_direction = new_direction / np.linalg.norm(new_direction)
		
		desired_direction = np.array([new_direction[0], new_direction[1], target_direction[2]])
		desired_direction = desired_direction / np.linalg.norm(desired_direction)
		
		return desired_direction
	
	def GetTargetDistance(self, current_position):
		target_position = self.waypoints[0]
		diff = target_position - current_position
		distance = np.linalg.norm(diff)
		
		return distance
	
	def GetWaypoint(self, current_position):
		
		while(len(self.waypoints) > 0):
			next_position = self.waypoints[0]
			distance = self.GetTargetDistance(current_position)
			
			if distance > self.waypoint_threshold:
				return next_position
			
			self.waypoints.pop(0)
			
		return current_position
	