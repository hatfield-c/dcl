
class EventQueue:
	def __init__(self):
		self.queue = []
		self.channels = {}
		
	def RegisterConsumer(self, consumer):
		
		channel_name = consumer.GetChannel()
		
		if channel_name not in self.channels:
			self.channels[channel_name] = [ consumer ]
		else:
			consumer_list = self.channels[channel_name]
			consumer_list.append(consumer)
		
	def AddEvent(self, channel_name, event_data):
		event = {
			"channel": channel_name,
			"data": event_data
		}
		
		self.queue.append(event)
		
	def ProcessQueue(self):
		
		for i in range(len(self.queue)):
			event = self.queue.pop(0)
			
			channel_name = event["channel"]
			event_data = event["data"]
			
			consumer_list = self.channels[channel_name]
			
			for consumer in consumer_list:
				consumer.Consume(event_data)