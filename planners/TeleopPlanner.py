import numpy as np
import pybullet as pb
import math
import random

import physics.Transform as Transform
import planners.PlannerInterface as PlannerInterface
import entities.SimpleEntity as SimpleEntity

class TeleopPlanner(PlannerInterface.PlannerInterface):

	def __init__(self, client_id, waypoints, time_counter, waypoint_threshold = 0.5, turn_strength = 1, debug = False):
		self.client_id = client_id
		self.waypoints = waypoints
		self.waypoint_threshold = waypoint_threshold
		self.turn_strength = turn_strength
		self.time_counter = time_counter

		self.current_action = "move"

		self.debug = debug
		self.waypoint_marker = None
		if debug:
			self.waypoint_marker = SimpleEntity.SimpleEntity(
				urdf_name = "entity_files/markers/green_diamond.urdf",
				client_id = self.client_id,
				position = [0, 0, -10],
			)

		self.drop_time = 280

	def GetPlan(self, sensors, metadata):
		xKey = ord('x')
		lKey = ord('l')
		sKey = ord('s')
		cKey = ord('c')
		zKey = ord('z')
		pKey = ord('p')
		keys = pb.getKeyboardEvents()
		
		next_position = np.array([0,0,0.01])
		if pKey in keys:
			next_position = np.array([0,0,0.1])
			print("p")
		if lKey in keys:
			next_position = np.array([0,0,-0.1])
			print("l")
		if sKey in keys:
			next_position = np.array([0,0.1,0])
			print("s")
		if xKey in keys:
			next_position = np.array([0,-0.1,0])
			print("x")
		if cKey in keys:
			next_position = np.array([0.1,0,0])
			print("c")
		if zKey in keys:
			next_position = np.array([-0.1,0,0])
			print("z")

		telemetry = sensors["telemetry"]

		sensor_data = telemetry.ReadSensor(None)

		current_position = sensor_data["position"]
		next_position = current_position + next_position
		print("Current location " + str(current_position))
		print("Going to: " + str(next_position))
		if self.debug:
			self.waypoint_marker.SetState({"position": next_position})

		diff = next_position - current_position
		distance = np.linalg.norm(diff)

		if distance == 0:
			distance = 1

		waypoint_direction = diff / distance

		velocity = sensor_data["velocity"]
		current_quat = sensor_data["quaternion"]

		desired_direction = self.GetDesiredForwardDirection(waypoint_direction, velocity)

		drop_package = False
		if self.drop_time < self.time_counter.GetCount():
			drop_package = True

		plan = {
			"move_action": self.current_action,
			"current_quat": current_quat,
			"current_altitude": current_position[2],
			"desired_direction": desired_direction,
			"desired_altitude": next_position[2],
			"velocity": velocity,
			"drop_package": drop_package
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
		unitFactor = np.linalg.norm(new_direction)
		if unitFactor.all() == 0:
			unitFactor = 1
		new_direction = new_direction / unitFactor

		unitFactor = np.array([new_direction[0], new_direction[1], target_direction[2]])
		if unitFactor.all() == 0:
			unitFactor = 1
		desired_direction = np.array([new_direction[0], new_direction[1], target_direction[2]]) / unitFactor

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

	def SetWaypoints(self, new_waypoints):
		self.waypoints = new_waypoints
