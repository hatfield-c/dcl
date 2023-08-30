
class EventConsumerInterface:
	def __init__(self):
		pass
	
	def GetChannel(self):
		raise NotImplementedError()
	
	def Consume(self, event_data):
		raise NotImplementedError()