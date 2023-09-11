import sensors.SensorInterface as SensorInterface

class TelemSensor(SensorInterface.SensorInterface):
	def __init__(self, entity):
		self.entity = entity
		    		
	def ReadSensor(self, control_data):
		sensorCall = {}
		position, rotation = self.entity.GetPositionRotation()
		velocity, angular_velocity = self.entity.GetAngularAndLinearVelocity()
		quaternion = self.entity.GetQuaternion()
		sensorCall["altimeter"] = position[2]
		sensorCall["gps"] = position
		sensorCall["gyro"] = rotation
		sensorCall["quat"] = quaternion
		sensorCall["velocity"] = velocity
		sensorCall["accel"] = angular_velocity
		return sensorCall