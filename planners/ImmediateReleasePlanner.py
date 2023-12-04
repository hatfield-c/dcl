import planners.PlannerInterface as PlannerInterface

class ImmediateReleasePlanner(PlannerInterface.PlannerInterface):

	def __init__(self):
		pass

	def GetPlan(self, sensors, metadata):

		plan = {
			"drop_package": True
		}

		return plan
