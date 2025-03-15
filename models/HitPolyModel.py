import torch
import numpy as np

import CONFIG

class HitPolyModel(torch.nn.Module):
	def __init__(self, dimensionality):
		super().__init__()

		self.dimensionality = dimensionality

		self.layer0 = torch.nn.Linear(self.dimensionality, 256).cuda()
		self.layer1 = torch.nn.Linear(256, 1).cuda()
		self.activation = torch.nn.ReLU()

		self.sigmoid = torch.nn.Sigmoid()

	def forward(self, data):

		out = self.layer0(data)
		out = self.activation(out)
		out = self.layer1(out)
		out = self.sigmoid(out)

		return out
