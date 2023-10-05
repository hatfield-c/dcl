
class EventConsumerInterface:
	def __init__(self):
		pass
	
	def GetChannel(self):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')
	
	def Consume(self, event_data):
		raise NotImplementedError(self.__class__.__name__ + ' is not implemented.')