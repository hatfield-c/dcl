
import planners.PlannerInterface as PlannerInterface

class SimplePlanner(PlannerInterface.PlannerInterface):
	def __init__(self, drone):
		self.drone = drone
	
	def GetPlan(self, sensors, metadata):
		telem = sensors["telem"]
		sensorCall = telem.ReadSensor(None)
		
		altitude = sensorCall["altimeter"]
		
		current_state = { "altitude": altitude }
		next_state = { "altitude": 1 }
		
		plan = [current_state, next_state]
		
		return plan