import pybullet as pb
import numpy as np
import math

import CONFIG
import controllers.ControllerInterface as ControllerInterface
import controllers.modules.Pid as Pid

class PidForwardController(ControllerInterface.ControllerInterface):
	def __init__(self, force_scale, torque_scale):
		self.force_scale = force_scale
		self.torque_scale = torque_scale
		
		self.unit_ball = {
			"zero": np.array([0, 0, 0]),
			"right": np.array([1, 0, 0]),
			"forward": np.array([0, 1, 0]),
			"up": np.array([0, 0, 1]),
			"left": np.array([-1, 0, 0]),
			"down": np.array([0, 0, -1]),
			"backward": np.array([0, -1, 0]),
		}
		
		nav_pitch = math.pi / 4
		nav_yaw = math.pi / 2
		nav_roll = math.pi / 4
		
		# (0: pitch, roll, yaw)
		self.nav_ball = {
			"up": np.array([0, 0, 0]),
			"right": np.array([-nav_pitch, 0, nav_yaw]),
			"forward": np.array([-nav_pitch, 0, 0]),
			"down": np.array([0, 0, 0]),
			"left": np.array([-nav_pitch, 0, -nav_yaw]),
			"backward": np.array([-nav_pitch, 0, 2 * nav_yaw]),
		}
		
		self.xy_corner_1 = np.array([1, -1, 0])
		self.xy_corner_2 = np.array([-1, -1, 0])
		self.corner_dist = self.xy_corner_1 - self.xy_corner_2
		self.corner_dist = np.linalg.norm(self.corner_dist)
		
		self.speed_val = 1
		self.move_angle = math.pi / 4
		self.move_depth = -np.sin(self.move_angle)
		
		self.deadzones = np.array([0.05, 0.05, 0.05]) * 0
		self.current_thrust = 0
		
		self.thrust_pid = Pid.Pid(
			p_scale = 5, 
			i_scale = 0, 
			d_scale = 0.5, 
			#debug = True
		)
		self.pitch_pid = Pid.Pid(
			p_scale = 1, 
			i_scale = 0, 
			d_scale = 2, 
			#debug = True
		)
		self.roll_pid = Pid.Pid(
			p_scale = 0.005, 
			i_scale = 0,
			d_scale = 2, 
			#debug = True
		)
		self.yaw_pid = Pid.Pid(
			p_scale = 0.8,
			i_scale = 0,
			d_scale = 5,
			#debug = True
		)
		

	def GetControlSignal(self, plan, metadata):
		current_rotation = plan["current_rotation"]
		current_altitude = plan["current_altitude"]
		current_direction = plan["current_direction"]
		desired_direction = plan["desired_direction"]
		desired_altitude = plan["desired_altitude"]
		
		velocity = plan["velocity"]
		
		current_quat = plan["current_quat"]
		
		current_rotate_matrix = pb.getMatrixFromQuaternion(current_quat)
		current_rotate_matrix = np.array(current_rotate_matrix)
		current_rotate_matrix = current_rotate_matrix.reshape((3, 3))
		
		#desired_direction = np.array([0.7071069, 0.7071069, 0])
		desired_direction = np.array([1, 0, 0])
		
		desired_xy = desired_direction[[0, 1]]
		current_xy = current_direction[[0, 1]]
		desired_xy = desired_xy / np.linalg.norm(desired_xy)
		current_xy = current_xy / np.linalg.norm(current_xy)
		
		roll_error = 1 - np.dot(desired_xy, current_xy)
		
		local_front = np.matmul(current_rotate_matrix, self.unit_ball["forward"])
		local_corner_1 = np.matmul(current_rotate_matrix, self.xy_corner_1)
		local_corner_2 = np.matmul(current_rotate_matrix, self.xy_corner_2)
		
		pitch_error = local_front[2] - self.move_depth
		yaw_error = local_corner_2[2] - local_corner_1[2]
		
		
		print("===results===")
		
		print(roll_error)
		print(current_xy)
		print(desired_xy)

		thrust_rpm = self.thrust_pid.ControlStep(current_altitude, desired_altitude, velocity[2])
		pitch_rpm = self.pitch_pid.ControlStep(pitch_error)
		roll_rpm = self.roll_pid.ControlStep(roll_error)
		yaw_rpm = self.yaw_pid.ControlStep(yaw_error)
		
		#thrust_rpm = 0.068
		thrust_rpm = 0
		#pitch_rpm = 0
		#roll_rpm = 0
		#yaw_rpm = 0
		
		input()
		
		motor_vals = self.MotorMixer(thrust_rpm, yaw_rpm, pitch_rpm, roll_rpm)
		
		return motor_vals
				
	def NavBall(self, unit_direction, start_ball, end_ball):
		
		direction_horiz_anchor = self.GetNavBallAnchor(unit_direction[0], start_ball["right"], start_ball["left"], self.deadzones[0])
		direction_depth_anchor = self.GetNavBallAnchor(unit_direction[1], start_ball["forward"], start_ball["backward"], self.deadzones[1])
		direction_vert_anchor = self.GetNavBallAnchor(unit_direction[2], start_ball["up"], start_ball["down"], self.deadzones[2])
		
		action_horiz_anchor = self.GetNavBallAnchor(unit_direction[0], end_ball["right"], end_ball["left"], self.deadzones[0])
		action_depth_anchor = self.GetNavBallAnchor(unit_direction[1], end_ball["forward"], end_ball["backward"], self.deadzones[1])
		action_vert_anchor = self.GetNavBallAnchor(unit_direction[2], end_ball["up"], end_ball["down"], self.deadzones[2])
		
		horiz_interpolation = np.linalg.norm(direction_horiz_anchor - unit_direction)
		depth_interpolation = np.linalg.norm(direction_depth_anchor - unit_direction)
		vert_interpolation = np.linalg.norm(direction_vert_anchor - unit_direction)
		
		interpolation_sum = horiz_interpolation + depth_interpolation + vert_interpolation
		
		horiz_interpolation = 1 - ((horiz_interpolation * 2) / interpolation_sum)
		depth_interpolation = 1 - ((depth_interpolation * 2) / interpolation_sum)
		vert_interpolation = 1 - ((vert_interpolation * 2) / interpolation_sum)
		
		navball_action = (horiz_interpolation * action_horiz_anchor) + (depth_interpolation * action_depth_anchor) + (vert_interpolation * action_vert_anchor)
		
		return navball_action
		
	def GetNavBallAnchor(self, direction_val, positive_anchor, negative_anchor, deadzone):
		if np.absolute(direction_val) < deadzone:
			return self.zero
		
		if direction_val < 0:
			return negative_anchor
		
		return positive_anchor
	
	def MotorMixer(self, thrust, yaw, pitch, roll):
		motor_vals = {}
		
		fr = thrust + yaw + pitch + roll
		fl = thrust - yaw + pitch - roll
		br = thrust - yaw - pitch + roll
		bl = thrust + yaw - pitch - roll
		
		#fr = thrust + pitch
		#fl = thrust + pitch
		#br = thrust - pitch
		#bl = thrust - pitch
		
		motor_vals["fr_rotor_force"] = fr * self.force_scale
		motor_vals["fl_rotor_force"] = fl * self.force_scale
		motor_vals["br_rotor_force"] = br * self.force_scale
		motor_vals["bl_rotor_force"] = bl * self.force_scale
		#motor_vals["torque"] = (-fr + fl - br + bl) * self.torque_scale
		
		motor_vals["torque"] = yaw * self.torque_scale
		
		return motor_vals
	
	def RotationToDirection(self, rotation):
		x = -np.sin(rotation[2]) * np.cos(rotation[0])
		y = np.cos(rotation[2]) * np.cos(rotation[0])
		z = np.sin(rotation[0])
		
		direction = np.array([x, y, z])
		magnitude = np.linalg.norm(direction)
		
		return direction / magnitude