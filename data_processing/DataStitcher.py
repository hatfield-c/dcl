
import torch

class DataStitcher:
	def __init__(self):
		pass

	def StitchData(
		self,
		state_data_path,
		max_data_path,
		value_data_path,
		client_count,
		file_type = ".pt"
	):
		state_data = None
		max_data = None
		value_data = None

		for i in range(client_count):
			state_path = state_data_path + "-" + str(i) + file_type
			max_path = max_data_path + "-" + str(i) + file_type
			value_path = value_data_path + "-" + str(i) + file_type

			client_state_data = torch.load(state_path)
			client_max_data = torch.load(max_path)
			client_value_data = torch.load(value_path)

			if state_data is None:
				state_data = client_state_data
				max_data = client_max_data
				value_data = client_value_data

				continue

			state_data = torch.cat((state_data, client_state_data))
			max_data = torch.maximum(max_data, client_max_data)
			value_data = torch.cat((value_data, client_value_data))

		state_path = state_data_path + file_type
		max_path = max_data_path + file_type
		value_path = value_data_path + file_type

		torch.save(state_data, state_path)
		torch.save(value_data, value_path)
		torch.save(max_data, max_path)

		print("\nComplete!")
		print("    Stitched together", client_count, "files.")
		print("")
		self.PrintMetaData(value_data)
		print("")
		print("    state path:", state_path)
		print("    max path:", max_path)
		print("    value path:", value_path)
		print("")
		print("    state shape:", state_data.shape)
		print("    max shape  :", max_data.shape)
		print("    value shape:", value_data.shape)
		print("")
		print("    max data:")
		print("        ", max_data)

	def PrintMetaData(self, value_data):

		one_count = 0
		neg_one_count = 0
		zero_count = 0
		positive_count = 0
		negative_count = 0

		avg_count = 0

		for i in range(value_data.shape[0]):
			value = value_data[i]

			if len(value.shape) < 1:
				value = [value]

			avg_count += value[0]

			#if value[0] >= 1:
			#	one_count += 1
			#elif value[0] <= -1:
			#	neg_one_count += 1
			if value[0] == 0.5:
				zero_count += 1
			elif value[0] > 0.5:
				positive_count += 1
			elif value[0] < 0.5:
				negative_count += 1

		avg_count = avg_count / value_data.shape[0]

		#print("    >+1 count:", one_count)
		#print("    <-1 count:", neg_one_count)
		print("     =0.5 count:", zero_count)
		print("     >0.5 count:", positive_count)
		print("     <0.5 count:", negative_count)
		print("    average :", avg_count)
