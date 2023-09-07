
import pybullet as pb

class RenderCamera:
	def __init__(
		self, 
		target_entity = None,
		distance = 2,
		yaw = 75,
		pitch = -20
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
		
		pb.resetDebugVisualizerCamera(
			cameraDistance = self.distance, 
			cameraYaw = self.yaw, 
			cameraPitch = self.pitch, 
			cameraTargetPosition = position
		)