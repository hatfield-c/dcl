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
		nav_yaw = math.pi / 4
		nav_roll = math.pi / 4
		
		# (0: pitch, roll, yaw)
		self.nav_ball = {
			"up": np.array([0, 0, 0]),
			"right": np.array([-nav_pitch, nav_roll, nav_yaw]),
			"forward": np.array([-nav_pitch, 0, 0]),
			"down": np.array([0, 0, 0]),
			"left": np.array([-nav_pitch, -nav_roll, -nav_yaw]),
			"backward": np.array([-nav_pitch, nav_roll, nav_yaw]),
		}
		
		self.deadzones = np.array([0.05, 0.05, 0.05]) * 0
		self.current_thrust = 0
		
		self.thrust_pid = Pid.Pid(
			p_scale = 5, 
			i_scale = 0.1, 
			d_scale = 0.5, 
			d_target = 0.5
		)
		self.pitch_pid = Pid.Pid(
			p_scale = 0.1, 
			i_scale = 0.1, 
			d_scale = 0.5, 
			d_target = 0.5
		)
		self.roll_pid = Pid.Pid(
			p_scale = 0.1, 
			i_scale = 0,#0.1, 
			d_scale = 0,#0.5, 
			d_target = 0.5
		)
		self.yaw_pid = Pid.Pid(
			p_scale = 0.1, 
			i_scale = 0,#0.1, 
			d_scale = 0,#0.5, 
			d_target = 0.5
		)
		

	def GetControlSignal(self, plan, metadata):
		current_rotation = plan["current_rotation"]
		current_altitude = plan["current_altitude"]
		desired_direction = plan["desired_direction"]
		desired_altitude = plan["desired_altitude"]
		angular_velocity = plan["angular_velocity"]
		velocity = plan["velocity"]
		
		#desired_direction = np.array([0, 1, 0])
		
		desired_rotation = self.NavBall(desired_direction, self.unit_ball, self.nav_ball)
		
		print("===results===")
		
		#print(current_rotation)
		#print(desired_rotation)
		#print(desired_direction)

		thrust_rpm = self.thrust_pid.ControlStep(current_altitude, desired_altitude, velocity[2])
		pitch_rpm = self.pitch_pid.ControlStep(current_rotation[0], desired_rotation[0], angular_velocity[0])
		roll_rpm = self.roll_pid.ControlStep(current_rotation[1], desired_rotation[1], angular_velocity[1])
		yaw_rpm = self.yaw_pid.ControlStep(current_rotation[2], desired_rotation[2], angular_velocity[2])
		
		#print(yaw_rpm)
		#thrust_rpm = 0.068
		#thrust_rpm = 0
		#yaw_rpm = 0
		#pitch_rpm = 0
		#roll_rpm = 0
		
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
		
		#print("===anchors===")
		#print(action_horiz_anchor)
		#print(action_depth_anchor)
		#print(action_vert_anchor)
		
		#print("===interpolations===")
		#print(horiz_interpolation)
		#print(depth_interpolation)
		#print(vert_interpolation)
		
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
		motor_vals["torque"] = (-fr + fl - br + bl) * self.torque_scale
		
		#motor_vals["torque"] = 0#yaw * self.torque_scale
		
		return motor_vals