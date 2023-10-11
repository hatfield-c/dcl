import observers.ObserverInterface as ObserverInterface

class CollisionResetObserver(ObserverInterface.ObserverInterface):
	def __init__(self, event_queue, channel_name, scenario):
		self.event_queue = event_queue
		self.entity_list = []
		self.channel_name = channel_name
		self.scenario = scenario

	def RegisterEntities(self, entity_list):
		for entity in entity_list:
			self.entity_list.append(entity)

	def Observe(self, timestep):
		collision_points = self.scenario.GetCollisionData()

		reset_scenario = False
		for i in range(len(self.entity_list)):
			for j in range(len(self.entity_list)):
				if i == j:
					continue

				entity1_bulletId = self.entity_list[i].GetBulletId()
				entity2_bulletId = self.entity_list[j].GetBulletId()

				for collision_data in collision_points:
					if collision_data[1] == entity1_bulletId and collision_data[2] == entity2_bulletId:
						observation = "Collision at time " + str(timestep) + " between " + str(self.entity_list[i].GetUrdf()) + " (Bullet ID: " + str(entity1_bulletId) + ") and " + str(self.entity_list[j].GetUrdf()) + " (Bullet ID: " + str(entity2_bulletId) + ")"
						# print(observation)
						self.event_queue.AddEvent(self.channel_name, observation)
						reset_scenario = True
		
		if reset_scenario == True:
			self.scenario.ResetScenario()
				

