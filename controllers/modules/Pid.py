
import numpy as np

import CONFIG

class Pid:
	def __init__(
		self,
		p_scale,
		i_scale,
		d_scale,
		integral_max = 2,
		d_limit = None,
		debug = False
	):
		self.p_scale = p_scale
		self.i_scale = i_scale
		self.d_scale = d_scale

		self.integral_max = integral_max
		self.d_limit = d_limit

		self.debug = debug

		self.memory = {
			"prev_value": 0,
			"estimated_velocity": 0,
			"integral": 0
		}

	def ControlStep(self, current, desired = 0, current_velocity = None):

		if current_velocity is None:
			current_velocity = self.memory["estimated_velocity"]

		error = desired - current

		p = error * self.p_scale

		self.memory["integral"] += error
		self.memory["integral"] = np.clip(self.memory["integral"], -self.integral_max, self.integral_max)
		i = self.memory["integral"] * self.i_scale

		d = current_velocity * self.d_scale

		if self.d_limit is not None:
			d = np.clip(d, self.d_limit[0], self.d_limit[1])

		pid = p + i + -d

		change = current - self.memory["prev_value"]
		self.memory["estimated_velocity"] = (self.memory["estimated_velocity"] / 3) + (2 * change / 3)
		self.memory["prev_value"] = current

		if self.debug:
			print("    pid:", pid)
			print("    p  :", p)
			print("    i  :", i)
			print("    d  :", d)

		return pid
