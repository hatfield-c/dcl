
import events.EventConsumerInterface as EventConsumerInterface

class ChannelLogger(EventConsumerInterface.EventConsumerInterface):
	
	def __init__(self, file_output_name, channel_name, newline = "\n"):
		self.file_output_name = file_output_name
		self.channel_name = channel_name
		self.newline = newline
		
	def GetChannel(self):
		return self.channel_name
	
	def Consume(self, channel_data):

		if (self.file_output_name == ""):
			return
		
		with open(self.file_output_name, 'a') as log_file:
			write_data = str(channel_data) + self.newline
			log_file.write(write_data)