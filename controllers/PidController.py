
import controllers.ControllerInterface as ControllerInterface

class PidController(ControllerInterface.ControllerInterface):
	def __init__(self):
		pass
	
	def GetControlSignal(self, plan, metadata):
		current_state = plan[0]
		next_state = plan[1]
		
		distance = current_state["distance"]
		diff = next_state["direction"] - current_state["direction"]
		
		yaw_error = 0
		
	def GetThrust(old_thrust):
		pass
	
	def GetYaw(old_yaw):
		pass
	
	def GetPitch(old_pitch):
		pass
	
	def GetRoll(old_roll):
		pass
	
	def MotorMixer(self, thrust, yaw, pitch, roll):
		motor_vals = {}
		
		motor_vals["fr"] = thrust + yaw + pitch + roll
		motor_vals["fl"] = thrust - yaw + pitch - roll
		motor_vals["br"] = thrust - yaw - pitch + roll
		motor_vals["bl"] = thrust + yaw - pitch - roll
		motor_vals["torque"] = -torques[0] + torques[1] - torques[2] + torques[3]
		
		return motor_vals