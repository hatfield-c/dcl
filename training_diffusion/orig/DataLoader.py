import time

import torch

class DataLoader:
	def __init__(self, samples, targets, episode_length, horizon, horizon_scale = 1):
		self.samples = samples.cuda()
		self.targets = targets.cuda()

		self.data_count = samples.shape[0]
		self.episode_length = episode_length
		self.horizon = horizon
		self.dimensionality = samples.shape[2]

		start = 0
		stop = horizon * horizon_scale
		step_size = horizon_scale

		self.max_step = self.episode_length - stop

		offset_matrix = torch.arange(start, stop, step_size)
		self.offset_matrix = offset_matrix

	def DrawTrainSamples(self, sample_count):
		chosen_indices = torch.randint(0, self.data_count, (sample_count,))
		offset = torch.randint(0, self.max_step, (1,))
		#offset = offset[0]

		offset_matrix = offset + self.offset_matrix

		#samples_orig = self.samples[chosen_indices, offset:(offset + self.horizon)]
		#samples_orig = self.samples[chosen_indices, offset_matrix]
		targets_orig = self.targets[chosen_indices]

		samples_orig = self.samples[chosen_indices]
		samples_orig = samples_orig[:, offset_matrix, :]

		return samples_orig, targets_orig
