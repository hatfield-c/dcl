import pybullet as pb
import SensorInterface

class AltimeterSensor(SensorInterface.SensorInterface):
	def __init__(self):
		pass
	
	def ReadSensor(self, control_data):
		position, orientation = pb.getBasePositionAndOrientation(control_data["pb_id"])
		
		return position[2]
		
		