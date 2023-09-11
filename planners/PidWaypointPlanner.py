import numpy as np
import math

import planners.PlannerInterface as PlannerInterface

class PidWaypointPlanner(PlannerInterface.PlannerInterface):
	
	def __init__(self, waypoints, waypoint_threshold = 0.5, alignment_threshold = 0.5):
		self.waypoints = waypoints
		self.waypoint_threshold = waypoint_threshold
		self.alignment_threshold = alignment_threshold
		
		self.HOVER_ACTION = "hover"
		self.MOVE_ACTION = "move"
		
		self.current_action = "hover"
		
	
	def GetPlan(self, sensors, metadata):
		"""
		gps = sensors["gps"]
		gyro = sensors["gyro"]
		quat = sensors["quat"]
		velocity_sensor = sensors["velocity"]
		"""
		telem = sensors["telem"]
		
		sensorCall = telem.ReadSensor(None)
		
		current_position = sensorCall["gps"]
		next_position = self.GetWaypoint(current_position)
		
		diff = next_position - current_position
		distance = np.linalg.norm(diff)
		
		if distance == 0:
			distance = 1
		
		desired_direction = diff / distance

		current_rotation = sensorCall["gyro"]
		current_direction = self.RotationToDirection(current_rotation)

		velocity = sensorCall["velocity"]
		current_quat = sensorCall["quat"]

		action = self.ChooseAction(current_position, current_direction, desired_direction)
		
		plan = {
			"action": action,
			"current_quat": current_quat,
			"current_altitude": current_position[2],
			"desired_direction": desired_direction, 
			"desired_altitude": next_position[2],
			"velocity": velocity
		}
		
		return plan
			
	def ChooseAction(self, current_position, current_direction, target_direction):
		return self.MOVE_ACTION
		
		target_distance = self.GetTargetDistance(current_position)
		alignment = np.dot(current_direction, target_direction)
		
		if target_distance > self.waypoint_threshold and alignment > self.alignment_threshold:
			return self.MOVE_ACTION
		
		return self.HOVER_ACTION
	
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
	
	def RotationToDirection(self, rotation):
		x = -np.sin(rotation[2]) * np.cos(rotation[0])
		y = np.cos(rotation[2]) * np.cos(rotation[0])
		z = np.sin(rotation[0])
		
		direction = np.array([x, y, z])
		magnitude = np.linalg.norm(direction)
		
		return direction / magnitude