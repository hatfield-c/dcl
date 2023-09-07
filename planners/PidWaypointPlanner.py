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
		gyro = sensors["gyro"]
		accelerometer = sensors["accelerometer"]
		velocity_sensor = sensors["velocity"]
		
		current_position = gps.ReadSensor(None)
		next_position = self.GetWaypoint(current_position)
		
		diff = next_position - current_position
		distance = np.linalg.norm(diff)
		
		if distance == 0:
			distance = 1
		
		desired_direction = diff / distance
		current_rotation = gyro.ReadSensor(None)
		
		velocity = velocity_sensor.ReadSensor(None)
		angular_velocity = accelerometer.ReadSensor(None)

		#print("===planner===")
		#print("dd     :", desired_direction)
		#print("current:", current_position)
		#print("next:", next_position)
		#print("===")

		plan = { 
			"current_rotation": current_rotation, 
			"current_altitude": current_position[2],
			"desired_direction": desired_direction, 
			"desired_altitude": next_position[2],
			"angular_velocity": angular_velocity,
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

	def DirectionToRotation(self, direction):
		pitch = math.asin(direction[1])
		yaw = math.atan2(direction[0], direction[2])
		
		return pitch, yaw

	def RotationToDirection(self, rotation):
		x = -np.sin(rotation[2]) * np.cos(rotation[0])
		y = np.cos(rotation[2]) * np.cos(rotation[0])
		z = np.sin(rotation[0])
		
		direction = np.array([x, y, z])
		magnitude = np.linalg.norm(direction)
		
		return direction / magnitude