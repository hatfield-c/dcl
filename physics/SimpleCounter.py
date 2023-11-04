
class SimpleCounter:
	def __init__(self, start_val = 0):
		self.count = start_val

	def Increment(self, amount = 1):
		self.count += amount

	def Reset(self, start_val = 0):
		self.count = start_val

	def GetCount(self):
		return self.count
