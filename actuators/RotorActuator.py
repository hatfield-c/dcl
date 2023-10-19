import numpy as np
import pybullet as pb

import actuators.ActuatorInterface as ActuatorInterface

class RotorActuator(ActuatorInterface.ActuatorInterface):
	def __init__(self):
		self.last_command = None

	def Actuate(self, control_data):

		self.last_command = np.array([
			control_data["thrust_signal"],
			control_data["pitch_signal"],
			control_data["roll_signal"],
			control_data["yaw_signal"],
		])

		pb.applyExternalForce(
			control_data["pb_id"],
			0,
			forceObj = [0, 0, control_data["fr_rotor_force"]],
			posObj = [0, 0, 0],
			flags = pb.LINK_FRAME
		)
		pb.applyExternalForce(
			control_data["pb_id"],
			1,
			forceObj = [0, 0, control_data["fl_rotor_force"]],
			posObj = [0, 0, 0],
			flags = pb.LINK_FRAME
		)
		pb.applyExternalForce(
			control_data["pb_id"],
			2,
			forceObj = [0, 0, control_data["br_rotor_force"]],
			posObj = [0, 0, 0],
			flags = pb.LINK_FRAME
		)
		pb.applyExternalForce(
			control_data["pb_id"],
			3,
			forceObj = [0, 0, control_data["bl_rotor_force"]],
			posObj = [0, 0, 0],
			flags = pb.LINK_FRAME
		)

		pb.applyExternalTorque(
			control_data["pb_id"],
			-1,
			torqueObj = [0, 0, control_data["torque"]],
			flags = pb.LINK_FRAME
		)

	def GetLastCommand(self):
		return self.last_command
