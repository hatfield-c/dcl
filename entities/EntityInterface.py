
class EntityInterface:
	def __init__(self):
		pass

	def UpdateEntity(self):
		raise NotImplementedError()

	def GetBulletId(self):
		raise NotImplementedError()

	def GetQuaternion(self):
		raise NotImplementedError()

	def GetUrdf(self):
		raise NotImplementedError()

	def GetPosition(self):
		raise NotImplementedError()

	def GetRotation(self):
		raise NotImplementedError()

	def GetVelocity(self):
		raise NotImplementedError()

	def GetAngularVeclotiy():
		raise NotImplementedError()

	def GetStatePermutation(self):
		raise NotImplementedError()

	def SetState(self, state_data):
		raise NotImplementedError()
