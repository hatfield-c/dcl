import pybullet as pb
import numpy as np
import math

import CONFIG
import physics.Transform as Transform
import controllers.ControllerInterface as ControllerInterface
import controllers.modules.Pid as Pid

class PidForwardController(ControllerInterface.ControllerInterface):
	def __init__(self, force_scale, torque_scale):
		self.force_scale = force_scale
		self.torque_scale = torque_scale

		self.xy_corner_1 = np.array([1, -1, 0])
		self.xy_corner_2 = np.array([-1, -1, 0])

		self.speed_val = 1
		self.move_angle = math.pi / 4
		self.move_depth = -np.sin(self.move_angle)

		self.thrust_pid = Pid.Pid(
			p_scale = 10,
			i_scale = 0.1,
			d_scale = 5,
			#debug = True
		)
		self.pitch_pid = Pid.Pid(
			p_scale = 1,
			i_scale = 0,#0.1,
			d_scale = 10,
			#debug = True
		)
		self.roll_pid = Pid.Pid(
			p_scale = 0.05,
			i_scale = 0.01,
			d_scale = 10,
			#debug = True
		)
		self.yaw_pid = Pid.Pid(
			p_scale = 0.8,
			i_scale = 0,
			d_scale = 10,
			#debug = True
		)

		self.thrust_multiplier = 1

	def GetControlSignal(self, plan, metadata):
		control_signal = {}

		move_action = plan["move_action"]

		if move_action == "move":
			control_signal = self.MoveAction(plan)

		return control_signal


	def MoveAction(self, plan):
		current_altitude = plan["current_altitude"]
		desired_direction = plan["desired_direction"]
		desired_altitude = plan["desired_altitude"]
		velocity = plan["velocity"]
		current_quat = plan["current_quat"]

		desired_xy = desired_direction[[0, 1]]
		unitFactor = np.linalg.norm(desired_xy)
		if unitFactor == 0:
			unitFactor = 1
		desired_xy = desired_xy / unitFactor

		local_front = Transform.GetForward(current_quat)
		local_corner_1 = Transform.RotatePoint(current_quat, self.xy_corner_1)
		local_corner_2 = Transform.RotatePoint(current_quat, self.xy_corner_2)

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

		control_data = self.MotorMixer(thrust_rpm, yaw_rpm, pitch_rpm, roll_rpm)

		#control_data["desired_direction"] = desired_direction[[0, 1]]
		#control_data["desired_altitude"] = desired_altitude
		control_data["drop_package"] = plan["drop_package"]
		#control_data["thrust_signal"] = thrust_rpm
		#control_data["pitch_signal"] = pitch_rpm
		#control_data["roll_signal"] = roll_rpm
		#control_data["yaw_signal"] = yaw_rpm

		return control_data

	def MotorMixer(self, thrust, yaw, pitch, roll):
		motor_vals = {}

		if thrust < 0:
			thrust = self.thrust_multiplier * thrust

		fr = thrust + yaw + pitch + roll
		fl = thrust - yaw + pitch - roll
		br = thrust - yaw - pitch + roll
		bl = thrust + yaw - pitch - roll

		#print("thrust:", thrust)
		#print(fr)
		#print(fl)
		#print(br)
		#print(bl)
		#print("==============")

		motor_vals["fr_rotor_force"] = fr * self.force_scale
		motor_vals["fl_rotor_force"] = fl * self.force_scale
		motor_vals["br_rotor_force"] = br * self.force_scale
		motor_vals["bl_rotor_force"] = bl * self.force_scale

		motor_vals["torque"] = yaw * self.torque_scale

		return motor_vals
