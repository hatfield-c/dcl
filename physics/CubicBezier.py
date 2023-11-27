import physics.QuadraticBezier as QuadraticBezier

class CubicBezier:
	def __init__(self, a0, a1, a2, a3):
		self.curve0 = QuadraticBezier.QuadraticBezier(a0, a1, a2)
		self.curve1 = QuadraticBezier.QuadraticBezier(a1, a2, a3)

	def GetPosition(self, t):
		b0 = self.curve0.GetPosition(t)
		b1 = self.curve1.GetPosition(t)

		return ((1 - t) * b0) + (t * b1)

	def SetPath(self, a0, a1, a2, a3):
		self.curve0 = QuadraticBezier.QuadraticBezier(a0, a1, a2)
		self.curve1 = QuadraticBezier.QuadraticBezier(a1, a2, a3)

	def GetControlPoints(self):
		control_points = [
			self.curve0.a0,
			self.curve0.a1,
			self.curve0.a2,
			self.curve1.a2
		]

		return control_points
