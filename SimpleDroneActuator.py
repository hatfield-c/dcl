import pybullet as pb

import ActuatorInterface

class SimpleDroneActuator(ActuatorInterface.ActuatorInterface):
	def __init__(self):
		pass
	
	def Actuate(self, control_data):
		
		pb.applyExternalForce(
			control_data["pb_id"],
			0,
			forceObj=[0, 0, control_data["fr_rotor_force"]],
			posObj=[0, 0, 0],
			flags=pb.LINK_FRAME
		)
		pb.applyExternalForce(
			control_data["pb_id"],
			1,
			forceObj=[0, 0, control_data["fl_rotor_force"]],
			posObj=[0, 0, 0],
			flags=pb.LINK_FRAME
		)
		pb.applyExternalForce(
			control_data["pb_id"],
			2,
			forceObj=[0, 0, control_data["br_rotor_force"]],
			posObj=[0, 0, 0],
			flags=pb.LINK_FRAME
		)
		pb.applyExternalForce(
			control_data["pb_id"],
			3,
			forceObj=[0, 0, control_data["bl_rotor_force"]],
			posObj=[0, 0, 0],
			flags=pb.LINK_FRAME
		)