import math

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

	def GetDistance(self, x1, y1, z1, x2, y2, z2):
		return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)

	def ProcessDistanceQueue(self, distance_range):
		event_package = self.queue.pop(0)
		event_target = self.queue.pop(0)

		channel_name = event_package["channel"]
		event_package_data = event_package["data"].split()
		package_x = float((event_package_data[2])[1:])
		package_y = float(event_package_data[3])
		package_z = float((event_package_data[4])[:-1])

		event_target_data = event_target["data"].split()
		target_x = float((event_target_data[2])[1:])
		target_y = float(event_target_data[3])
		target_z = float((event_target_data[4])[:-1])

		target_distance = self.GetDistance(package_x, package_y, package_z, target_x, target_y, target_z)

		# print(event_package["data"])
		# print(package_x, package_y, package_z)
		# print(event_target["data"])
		# print(target_x, target_y, target_z)
		# print(target_distance)
		
		if target_distance <= distance_range:
			print(str(target_distance))
			event_data = event_target_data[0] + " " + str(target_distance)

			consumer_list = self.channels[channel_name]
			
			for consumer in consumer_list:
				consumer.Consume(event_data)
		
	def ProcessQueue(self):
		for i in range(len(self.queue)):
			event = self.queue.pop(0)
			
			channel_name = event["channel"]
			event_data = event["data"]
			
			consumer_list = self.channels[channel_name]
			
			for consumer in consumer_list:
				consumer.Consume(event_data)