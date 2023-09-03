
import controllers.ControllerInterface as ControllerInterface

class SimpleController(ControllerInterface.ControllerInterface):
	def __init__(self):
		pass
	
	def GetControlSignal(self, plan, metadata):
		current_state = plan[0]
		next_state = plan[1]
		
		altitude = current_state["altitude"]
		
		force = 0
		if altitude < 0.8:
			force = 0.2
		
		if altitude > 0.8:
			force = 0.06
		
		rotor_control = {
			"pb_id": metadata["pb_id"],
			"fr_rotor_force": force,
			"fl_rotor_force": force,
			"br_rotor_force": force,
			"bl_rotor_force": force,
			"torque": 0
		}
		
		return rotor_control