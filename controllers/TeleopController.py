import pybullet as pb
import numpy as np
import math
import keyboard

import CONFIG
import physics.Transform as Transform
import controllers.ControllerInterface as ControllerInterface
import controllers.modules.Pid as Pid


class TeleopController(ControllerInterface.ControllerInterface):
	def __init__(self, force_scale, torque_scale):
		self.force_scale = force_scale
		self.torque_scale = torque_scale

		self.xy_corner_1 = np.array([1, -1, 0])
		self.xy_corner_2 = np.array([-1, -1, 0])

		self.speed_val = 1
		self.move_angle = math.pi / 4
		self.move_depth = -np.sin(self.move_angle)
		"""
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
		"""

	def GetControlSignal(self, plan, sensors):
		telemetry = sensors["telemetry"]
		sensor_data = telemetry.ReadSensor(None)
		current_position = sensor_data["position"]
		current_rotation = sensor_data["rotation"]

		
		motor_vals = self.MoveAction(plan, current_position, current_rotation)

		return motor_vals


	def MoveAction(self, plan, current_position, current_rotation):
		max_pitch_forward = 30
		max_roll_right = 30
		max_pitch_backwards = -30
		max_roll_left = -30
		max_thrust = 3
		roll = current_rotation[0]
		pitch = current_rotation[1]
		pitch_rpm = 0
		thrust_rpm = 0
		roll_rpm = 0
		yaw_rpm = 0

		print("roll = " + str(roll) + "\n")
		print("pitch = " + str(pitch) + "\n")
		
		# if pitch is not max, turn that way
		# if thrust is less than max, increase thrust
		# if nothing is pressed, move all values towards zero
		something_pressed = False

		#if forward pressed
		'''
		if keyboard.is_pressed('w'):
			something_pressed = True
			if (pitch < max_pitch_forward):
				pitch_rpm = 100
		#if back pressed
		if keyboard.is_pressed('s'):
			something_pressed = True
			if (pitch > max_pitch_backwards):
				pitch_rpm = -100
		#if right pressed
		if keyboard.is_pressed('d'):
			something_pressed = True
			if (roll < max_roll_right):
				roll_rpm  = 100
		#if left pressed
		if keyboard.is_pressed('a'):
			something_pressed = True
			if (roll > max_roll_left):
				roll_rpm = -100
		#if nothing pressed
		if (something_pressed == False):
			if (pitch > 0):
				pitch_rpm = -100
			if (pitch < 0):
				pitch_rpm = 100
			if (roll > 0):
				roll_rpm = -100
			if (roll < 0):
				roll_rpm = 100
		if keyboard.is_pressed('q'):
			yaw_rpm = -100
		if keyboard.is_pressed('e'):
			yaw_rpm = 100

		if keyboard.is_pressed('space'):
			thrust_rpm = 100
		'''
		#yaw_rpm = 0.1 good exp. value
		'''
		roll_rpm = 0
		pitch_rpm = 0
		if (roll > 0 ):
			print("Max roll right reached, stopping rolling")
			roll_rpm = -0.01
		if (roll < 0):
			print("Max roll left reached, stopping rolling")
			roll_rpm = 0.01
		'''
		'''
		if (pitch > 0 ):
			print("Max pitch forward reached, stopping pitching")
			pitch_rpm = -0.1
		if (pitch < 0):
			print("Max pitch backward reached, stopping pitching")
			pitch_rpm = 0.1
		'''
		'''
		thrust_rpm = 0.1
		thrust_rpm = max(0, thrust_rpm)
		'''
		
		#if e pressed (turn right)
		#if q pressed (turn left)
		""""
		current_altitude = plan["current_altitude"]
		desired_direction = plan["desired_direction"]
		desired_altitude = plan["desired_altitude"]
		velocity = plan["velocity"]
		current_quat = plan["current_quat"]

		desired_xy = desired_direction[[0, 1]]
		desired_xy = desired_xy / np.linalg.norm(desired_xy)

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

		
		"""
		wKey = ord('w')
		aKey = ord('a')
		sKey = ord('s')
		dKey = ord('d')
		qKey = ord('q')
		eKey = ord('e')
		pKey = ord('p')
		keys = pb.getKeyboardEvents()
		if pKey in keys:
			thrust_rpm = 2
		if qKey in keys:
			yaw_rpm = 0.1
		if eKey in keys:
			yaw_rpm = -0.1
		if wKey in keys:
			pitch_rpm = 0.1
		if sKey in keys:
			pitch_rpm = -0.1
		if aKey in keys:
			roll_rpm = -0.1
		if dKey in keys:
			roll_rpm = 0.1


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
