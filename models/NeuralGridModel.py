import torch
import numpy as np

import CONFIG

class NeuralGridModel(torch.nn.Module):
	def __init__(self, dimensionality):
		super().__init__()

		self.dimensionality = 6#dimensionality

		self.layer0 = torch.nn.Linear(self.dimensionality, 2048).cuda()
		self.layer1 = torch.nn.Linear(2048, 1).cuda()
		self.activation = torch.nn.ReLU()

		self.sigmoid = torch.nn.Sigmoid()

	def forward(self, data):

		out = self.layer0(data)
		out = self.activation(out)
		out = self.layer1(out)
		out = self.sigmoid(out)

		return out

	def SaveParameters(self, save_path):
		model_data = self.state_dict()
		
		w0 = model_data["layer0.weight"].cpu()
		b0 = model_data["layer0.bias"].cpu()
		w1 = model_data["layer1.weight"].cpu()
		b1 = model_data["layer1.bias"].cpu()
		s0 = w0.shape
		
		print(s0)
		for j in range(2):
			for i in range(6):			
				print("{:.2f}".format(w0[j, i].item()) + ", ", end = "")
			
			print("")		
		print("")
		
		for j in range(254, 256):
			for i in range(6):
				print("{:.2f}".format(w0[j, i].item()) + ", ", end = "")
				
			print("")		
		print("\n")
		
		#w0 = w0.transpose(0, 1)
		#w1 = w1.transpose(0, 1)
		w0 = w0.flatten()
		w1 = w1.flatten()
		s0 = w0.shape
		
		w0 = w0.numpy()
		b0 = b0.numpy()
		w1 = w1.numpy()
		b1 = b1.numpy()
		
		w0 = w0.astype(np.float32)
		b0 = b0.astype(np.float32)
		w1 = w1.astype(np.float32)
		b1 = b1.astype(np.float32)
		
		w0.tofile(save_path + "w0.float")
		b0.tofile(save_path + "b0.float")
		w1.tofile(save_path + "w1.float")
		b1.tofile(save_path + "b1.float")
		
		print(s0)
		for i in range(12):
			print("{:.2f}".format(w0[i]) + ", ", end = "")
			
			if i == 5:
				print("")		
		print("\n")
		
		for i in range(12):
			index = (6 * 256) - (12 - i)
			print("{:.2f}".format(w0[index]) + ", ", end = "")
			
			if i == 5:
				print("")		
		print("")