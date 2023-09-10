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
		
		self.xy_corner_1 = np.array([1, -1, 0])
		self.xy_corner_2 = np.array([-1, -1, 0])
		
		self.speed_val = 1
		self.move_angle = math.pi / 4
		self.move_depth = -np.sin(self.move_angle)
		
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
			p_scale = 0.05, 
			i_scale = 0,
			d_scale = 1, 
			#debug = True
		)
		self.yaw_pid = Pid.Pid(
			p_scale = 0.8,
			i_scale = 0,
			d_scale = 5,
			#debug = True
		)
		

	def GetControlSignal(self, plan, metadata):
		action = plan["action"]
		
		if action == "hover":
			motor_vals = self.HoverAction(plan)
		if action == "move":
			motor_vals = self.MoveAction(plan)
		
		return motor_vals
		
	def HoverAction(self, plan):
		current_altitude = plan["current_altitude"]
		desired_direction = plan["desired_direction"]
		desired_altitude = plan["desired_altitude"]
		velocity = plan["velocity"]
		current_quat = plan["current_quat"]
		
		current_rotate_matrix = pb.getMatrixFromQuaternion(current_quat)
		current_rotate_matrix = np.array(current_rotate_matrix)
		current_rotate_matrix = current_rotate_matrix.reshape((3, 3))
		
		desired_xy = desired_direction[[0, 1]]
		desired_xy = desired_xy / np.linalg.norm(desired_xy)
		
		local_front = np.matmul(current_rotate_matrix, self.unit_ball["forward"])
		local_corner_1 = np.matmul(current_rotate_matrix, self.xy_corner_1)
		local_corner_2 = np.matmul(current_rotate_matrix, self.xy_corner_2)
		
		local_corner_1_xy = local_corner_1[[0, 1]]
		local_corner_2_xy = local_corner_2[[0, 1]]
		local_corner_1_xy = local_corner_1_xy / np.linalg.norm(local_corner_1_xy)
		local_corner_2_xy = local_corner_2_xy / np.linalg.norm(local_corner_2_xy)
		
		dist_1_xy = desired_xy - local_corner_1_xy
		dist_2_xy = desired_xy - local_corner_2_xy
		dist_1_xy = np.linalg.norm(dist_1_xy)
		dist_2_xy = np.linalg.norm(dist_2_xy)
		
		pitch_error = local_front[2]
		roll_error = dist_2_xy - dist_1_xy
		yaw_error = local_corner_2[2] - local_corner_1[2]
		
		thrust_rpm = self.thrust_pid.ControlStep(current_altitude, desired_altitude, velocity[2])
		pitch_rpm = self.pitch_pid.ControlStep(pitch_error)
		roll_rpm = self.roll_pid.ControlStep(roll_error)
		yaw_rpm = self.yaw_pid.ControlStep(yaw_error)
		
		thrust_rpm = max(0, thrust_rpm)
		
		motor_vals = self.MotorMixer(thrust_rpm, yaw_rpm, pitch_rpm, roll_rpm)
		
		return motor_vals
	
	def MoveAction(self, plan):
		current_altitude = plan["current_altitude"]
		desired_direction = plan["desired_direction"]
		desired_altitude = plan["desired_altitude"]
		velocity = plan["velocity"]
		current_quat = plan["current_quat"]
		
		current_rotate_matrix = pb.getMatrixFromQuaternion(current_quat)
		current_rotate_matrix = np.array(current_rotate_matrix)
		current_rotate_matrix = current_rotate_matrix.reshape((3, 3))
		
		desired_xy = desired_direction[[0, 1]]
		desired_xy = desired_xy / np.linalg.norm(desired_xy)
		
		local_front = np.matmul(current_rotate_matrix, self.unit_ball["forward"])
		local_corner_1 = np.matmul(current_rotate_matrix, self.xy_corner_1)
		local_corner_2 = np.matmul(current_rotate_matrix, self.xy_corner_2)
		
		local_corner_1_xy = local_corner_1[[0, 1]]
		local_corner_2_xy = local_corner_2[[0, 1]]
		local_corner_1_xy = local_corner_1_xy / np.linalg.norm(local_corner_1_xy)
		local_corner_2_xy = local_corner_2_xy / np.linalg.norm(local_corner_2_xy)
		
		dist_1_xy = desired_xy - local_corner_1_xy
		dist_2_xy = desired_xy - local_corner_2_xy
		dist_1_xy = np.linalg.norm(dist_1_xy)
		dist_2_xy = np.linalg.norm(dist_2_xy)
		
		pitch_error = local_front[2] - self.move_depth
		roll_error = dist_2_xy - dist_1_xy
		yaw_error = local_corner_2[2] - local_corner_1[2]
			
		thrust_rpm = self.thrust_pid.ControlStep(current_altitude, desired_altitude, velocity[2])
		pitch_rpm = self.pitch_pid.ControlStep(pitch_error)
		roll_rpm = self.roll_pid.ControlStep(roll_error)
		yaw_rpm = self.yaw_pid.ControlStep(yaw_error)
		
		thrust_rpm = max(0, thrust_rpm)
		
		motor_vals = self.MotorMixer(thrust_rpm, yaw_rpm, pitch_rpm, roll_rpm)
		
		return motor_vals
	
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
		
		motor_vals["torque"] = yaw * self.torque_scale
		
		return motor_vals
	