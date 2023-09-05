import numpy as np

import CONFIG
import controllers.ControllerInterface as ControllerInterface

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
		
		turn_thrust = 0.1
		turn_pitch = 0.1
		
		# todo: rename this to be self documenting
		# (0: thrust, yaw, pitch)
		self.nav_ball = {
			"up": np.array([1, 0, 0]),
			"right": np.array([turn_thrust, 1, -turn_pitch]),
			"forward": np.array([turn_thrust, 0, -turn_pitch]),
			"down": np.array([-1, 0, 0]),
			"left": np.array([turn_thrust, -1, -turn_pitch]),
			"backward": np.array([turn_thrust, 0, turn_pitch]),
		}
		
		self.dir_ball = {
			"up": np.array([0, 0, 1]),
			"right": np.array([0, ]),
			"forward": np.array([0, 0, 0])
		}
		
		self.deadzones = np.array([0.05, 0.05, 0.05]) * 0
		
		self.current_thrust = 0
		
		self.pitch_pid = {
			"p": 1,
			"i": 2,
			"d": 2
		}
		self.pitch_memory = {
			"prev_pitch": 0,
			"integral": 0
		}
	
	def GetControlSignal(self, plan, metadata):
		current_state = plan[0]
		next_state = plan[1]
		
		distance = current_state["distance"]
		current_direction = current_state["direction"]
		desired_direction = next_state["direction"]
		
		#test_direction = np.array([1, 0, 0])
		#test_direction = test_direction / np.linalg.norm(test_direction)
		
		navball_current = self.NavBall(current_direction, self.unit_ball, self.nav_ball)
		navball_action = self.NavBall(desired_direction, self.unit_ball, self.nav_ball)
		#navball_action = self.NavBall(test_direction)
		print("===results===")
		#print(test_direction, navball_action)
		print(navball_current, navball_action)
		#print(current_direction)
		input()
		thrust_rpm = navball_action[0]
		yaw_rpm = navball_action[1]
		pitch_rpm = self.GetPitchRpm(navball_current[2], navball_action[2])
		roll_rpm = 0
		
		motor_vals = self.MotorMixer(thrust_rpm, yaw_rpm, pitch_rpm, roll_rpm)
		
		return motor_vals
				
	def GetThrustRpm(self, current, desired):
		pass
	
	def GetYawRpm(self, current, desired):
		pass
	
	def GetPitchRpm(self, current, desired):
		
		error = desired - current
		
		self.pitch_memory["integral"] += error
		self.pitch_memory["integral"] = np.clip(self.pitch_memory["integral"], 2, -2)
		
		error_scaled = error / self.pitch_pid["i"]
		current_scaled = error * self.pitch_pid["d"]
		
		i = (error_scaled * CONFIG.timestep) + self.pitch_memory["integral"]
		d = (current_scaled - self.pitch_memory["prev_pitch"])
		
		self.pitch_memory["prev_pitch"] = current
		
		pid = error + i - d
		pid = pid * self.pitch_pid["p"]
		
		return pid
	
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
		
		motor_vals["fr_rotor_force"] = fr * self.force_scale
		motor_vals["fl_rotor_force"] = fl * self.force_scale
		motor_vals["br_rotor_force"] = br * self.force_scale
		motor_vals["bl_rotor_force"] = bl * self.force_scale
		motor_vals["torque"] = (-fr + fl - br + bl) * self.torque_scale
		
		return motor_vals