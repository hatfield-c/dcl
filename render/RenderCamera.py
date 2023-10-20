
import pybullet as pb
import math

class RenderCamera:
	def __init__(
		self,
		target_entity = None,
		distance = 3,
		yaw = None,
		pitch = None
	):
		self.target_entity = target_entity
		self.distance = distance
		self.yaw = yaw
		self.pitch = pitch

		self.offset = 0

	def SetTarget(
		self,
		target_entity
	):
		self.target_entity = target_entity

	def FollowTarget(self):
		#if self.target_entity is None:
		#	return

		position = self.target_entity.GetPosition()
		rotation = self.target_entity.GetRotation()

		yaw = self.yaw
		pitch = self.pitch

		if yaw is None:
			yaw = rotation[2] * (180 / math.pi)

		if pitch is None:
			pitch = rotation[0] * (180 / math.pi)

		pb.resetDebugVisualizerCamera(
			cameraDistance = self.distance,
			cameraYaw = yaw,
			cameraPitch = pitch,
			cameraTargetPosition = position
		)
