import numpy as np
import pybullet as pb
import time

import physics.Transform as Transform
import sensors.SensorInterface as SensorInterface

class LidarSensor(SensorInterface.SensorInterface):
	def __init__(
			self,
			client_id,
			entity,
			offset = [0.1,0,0],
			debug = False,
			debug_time_buffer = 0.003
		):
		self.client_id = client_id
		self.entity = entity
		self.offset = offset
		self.offset_distance = np.linalg.norm(self.offset)

		self.debug = debug
		self.avg_render_time = 0
		self.current_time = time.time()
		self.debug_time_buffer = debug_time_buffer

		magnitude = self.offset_distance
		if magnitude == 0:
			magnitude = 1

		self.offset_direction = self.offset / magnitude

	def ReadSensor(self, control_data):
		position = control_data["position"]
		quaternion = control_data["quaternion"]

		beam_direction = Transform.RotateDirection(quaternion, self.offset_direction)
		beam_offset = beam_direction * self.offset_distance
		beam_origin = position + beam_offset
		beam_endpoint = beam_origin + beam_direction * 10

		results = pb.rayTest(beam_origin, beam_endpoint, self.client_id)
		results = results[0]
		target_id = results[0]

		hit_length = -1
		render_color = [0, 1, 0]

		if target_id >= 0:
			hit_position = results[3]
			hit_fraction = results[2]
			hit_length = 10 * hit_fraction

			beam_endpoint = hit_position
			render_color = [1, 0, 0]

			# print("hit at " + str(hit_length))

		time_diff = time.time() - self.current_time
		self.current_time = time.time()
		self.avg_render_time = (self.avg_render_time + time_diff) / 2

		if self.debug:
			pb.addUserDebugLine(
				beam_origin,
				beam_endpoint,
				lineColorRGB = render_color,
				lifeTime = time_diff + self.debug_time_buffer
			)


		return hit_length
