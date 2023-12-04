import time

import torch

class DataLoader:
	def __init__(self, samples, targets):
		self.samples = samples.cuda()
		self.targets = targets.cuda()

		print("[Samples Shape]:", self.samples.shape)

		self.data_count = samples.shape[0]
		self.dimensionality = samples.shape[1]

	def DrawSamples(self, sample_count):
		chosen_indices = torch.randint(0, self.data_count, (sample_count,))

		samples_orig = self.samples[chosen_indices]
		targets_orig = self.targets[chosen_indices]

		return samples_orig, targets_orig
