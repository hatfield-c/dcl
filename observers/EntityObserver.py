
import observers.ObserverInterface as ObserverInterface

class EntityObserver(ObserverInterface.ObserverInterface):
	def __init__(self, event_queue, channel_name):
		self.event_queue = event_queue
		self.entity_list = []
		self.channel_name = channel_name
		
	def RegisterEntities(self, entity_list):
		for entity in entity_list:
			self.entity_list.append(entity)
		
	def Observe(self, timestep):
		for i in range(len(self.entity_list)):
			entity = self.entity_list[i]
			
			pb_id = entity.GetBulletId()
			object_name = entity.GetUrdf()
			position = entity.GetPosition()
			
			observation = str(timestep) + " [" + str(pb_id) + "_" + str(object_name) + "] " + str(position)
			
			self.event_queue.AddEvent(self.channel_name, observation)