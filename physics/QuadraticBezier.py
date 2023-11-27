

class QuadraticBezier:
	def __init__(self, a0, a1, a2):
		self.a0 = a0
		self.a1 = a1
		self.a2 = a2

	def GetPosition(self, t):
		a0 = self.a0
		a1 = self.a1
		a2 = self.a2

		return a1 + ((1 - t) ** 2) * (a0 - a1) + (t ** 2) * (a2 - a1)

	def SetPath(self, a0, a1, a2):
		self.a0 = a0
		self.a1 = a1
		self.a2 = a2
