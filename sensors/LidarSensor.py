import numpy as np
import pybullet as pb
import physics.Transform as Transform

import sensors.SensorInterface as SensorInterface

class LidarSensor(SensorInterface.SensorInterface):
	def __init__(
			self, 
			entity, 
			offset = [0.1,0,0]
		):
		self.entity = entity
		self.offset = offset
		self.offset_distance = np.linalg.norm(self.offset)

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

		results = pb.rayTest(beam_origin, beam_endpoint)
		results = results[0]
		target_id = results[0]
		if (target_id < 0):
			pb.addUserDebugLine(beam_origin, beam_endpoint, lineColorRGB=[1, 0, 0], lifeTime=0.2)
			hit_length = -1
		else:
			hitPosition = results[3]
			pb.addUserDebugLine(beam_origin, hitPosition, lineColorRGB=[0, 1, 0], lifeTime=0.2)
			hit_fraction = results[2]
			hit_length = 10 * hit_fraction
			print("hit at " + str(hit_length))
			
		return hit_length
