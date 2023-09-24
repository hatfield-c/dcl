import sensors.SensorInterface as SensorInterface

class TelemetrySensor(SensorInterface.SensorInterface):
	def __init__(self, entity):
		self.entity = entity

	def ReadSensor(self, control_data):
		sensor_data = {}

		sensor_data["position"] = self.entity.GetPosition()
		sensor_data["rotation"] = self.entity.GetRotation()
		sensor_data["velocity"] = self.entity.GetVelocity()
		sensor_data["angular_velocity"] = self.entity.GetAngularVelocity()
		sensor_data["quaternion"] = self.entity.GetQuaternion()

		return sensor_data
