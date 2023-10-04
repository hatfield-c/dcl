import math
import observers.ObserverInterface as ObserverInterface

class TargetDistanceObserver(ObserverInterface.ObserverInterface):
	def __init__(self, event_queue, channel_name, event_distance_range):
		self.event_queue = event_queue
		self.channel_name = channel_name
		self.event_distance_range = event_distance_range

	def RegisterTarget(self, target_entity):
		self.target_entity = target_entity

	def RegisterPackage(self, package_entity):
		self.package_entity = package_entity

	def GetDistance(self, target_position, package_position):
		return math.sqrt((target_position[0] - package_position[0]) ** 2 + (target_position[1] - package_position[1]) ** 2 + (target_position[2] - package_position[2]) ** 2)

	def Observe(self, timestep):
		target_position = self.target_entity.GetPosition()
		package_position = self.package_entity.GetPosition()
		
		package_distance_to_target = self.GetDistance(target_position, package_position)
		# package_distance_to_target = 0

		# print(package_position)

		if package_distance_to_target <= self.event_distance_range:
			observation = str(timestep) + " Distance: " + str(package_distance_to_target) + " Target: " + str(target_position) + " Package: " + str(package_position)
			self.event_queue.AddEvent(self.channel_name, observation)