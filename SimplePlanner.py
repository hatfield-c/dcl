
import PlannerInterface

class SimplePlanner(PlannerInterface.PlannerInterface):
	def __init__(self):
		pass
	
	def GetPlan(self, sensors, metadata):
		
		sensor_control = { "pb_id": metadata["pb_id"] }
		altimeter = sensors["altimeter"]
		
		altitude = altimeter.ReadSensor(sensor_control)
		
		current_state = { "altitude": altitude }
		next_state = { "altitude": 1 }
		
		plan = [current_state, next_state]
		
		return plan