
import events.EventConsumerInterface as EventConsumerInterface

class SimpleTimeConsumer(EventConsumerInterface.EventConsumerInterface):
	def __init__(self):
		self.channel = "simple_time"
		
	def GetChannel(self):
		return self.channel
	
	def Consume(self, event_data):
		print(event_data)