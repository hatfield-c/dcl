
import numpy as np

import CONFIG

class Pid:
	def __init__(
		self,
		p_scale,
		i_scale,
		d_scale,
		integral_max = 2,
		d_target = 0.5,
		debug = False
	):
		self.p_scale = p_scale
		self.i_scale = i_scale
		self.d_scale = d_scale
		
		self.integral_max = integral_max
		self.d_target = d_target
		
		self.debug = debug
		
		self.memory = {
			"integral": 0
		}
		
	def ControlStep(self, current, desired, current_velocity):
		error = desired - current
		
		p = error * self.p_scale
		
		self.memory["integral"] += error
		self.memory["integral"] = np.clip(self.memory["integral"], -self.integral_max, self.integral_max)
		i = self.memory["integral"] * self.i_scale
		
		desired_velocity = error * self.d_target
		d_error = desired_velocity - current_velocity
		d = d_error * self.d_scale
		
		pid = p + i + d

		if self.debug:
			print("    pid:", pid)
			print("    p  :", p)
			print("    i  :", i)
			print("    d  :", d)

		return pid