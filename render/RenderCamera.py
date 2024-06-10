
import pybullet as pb
import numpy as np
import math

class RenderCamera:
	def __init__(
		self,
		client_id,
		target_entity = None,
		distance = 3,
		yaw = None,
		pitch = None
	):
		self.client_id = client_id
		self.target_entity = target_entity
		self.distance = distance
		self.yaw = yaw
		self.pitch = pitch

		self.offset = 0

	def SetAngle(self, yaw, pitch):
		self.yaw = yaw
		self.pitch = pitch

	def SetTarget(self, target_entity):
		self.target_entity = target_entity

	def SetCamera(self, position):
		pb.resetDebugVisualizerCamera(
			cameraDistance = self.distance,
			cameraYaw = self.yaw,
			cameraPitch = self.pitch,
			cameraTargetPosition = position,
			physicsClientId = self.client_id
		)

	def FollowTarget(self):
		if self.target_entity is None:
			return
		
		position = self.target_entity.GetCameraPosition()
		rotation = self.target_entity.GetRotation()

		yaw = self.yaw
		pitch = self.pitch

		if yaw is None:
			position_magnitude = np.linalg.norm(position)

			if position_magnitude == 0:
				yaw = 0
			else:
				ratio = position[0] / position[1]

				yaw = math.atan(ratio)
				yaw = yaw * (180 / math.pi)

				if position[1] > 0:
					yaw = 180 - yaw

				if position[1] < 0:
					yaw = -yaw

		if pitch is None:
			pitch = rotation[0] * (180 / math.pi)

		pb.resetDebugVisualizerCamera(
			cameraDistance = self.distance,
			cameraYaw = yaw,
			cameraPitch = pitch,
			cameraTargetPosition = position,
			physicsClientId = self.client_id
		)
