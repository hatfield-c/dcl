import torch
import numpy as np

import CONFIG

class HitPolyModel(torch.nn.Module):
	def __init__(self, dimensionality):
		super().__init__()

		self.dimensionality = dimensionality
		self.hidden_units = 128

		self.layer0 = torch.nn.Linear(self.dimensionality, 64).cuda()
		self.layer1 = torch.nn.Linear(64, 128).cuda()
		self.layer2 = torch.nn.Linear(128, 64).cuda()
		self.layer3 = torch.nn.Linear(64, 16).cuda()
		self.layer4 = torch.nn.Linear(16, 1).cuda()
		self.activation = torch.nn.ReLU()
		#self.activation = torch.nn.Mish()
		self.sigmoid = torch.nn.Sigmoid()

	def forward(self, data):

		out = self.layer0(data)
		out = self.activation(out)
		out = self.layer1(out)
		out = self.activation(out)
		out = self.layer2(out)
		out = self.activation(out)
		out = self.layer3(out)
		out = self.activation(out)
		out = self.layer4(out)
		out = self.sigmoid(out)

		return out
