
class EntityInterface:
	def __init__(self):
		pass

	def UpdateEntity(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def GetBulletId(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def GetQuaternion(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def GetUrdf(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def GetPosition(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def GetRotation(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def GetVelocity(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def GetAngularVeclotiy(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def GetStatePermutation(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')

	def SetState(self, state_data):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')
