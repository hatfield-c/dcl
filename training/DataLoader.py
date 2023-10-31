import time

import math
import torch
import numpy as np
import random

import training.CONFIG

class DataLoader:
	def __init__(self, samples, targets, horizon, episode_length = 100):
		self.samples = samples.cuda()
		self.targets = targets.cuda()

		self.data_count = samples.shape[0]
		self.episode_length = episode_length
		self.horizon = horizon
		self.dimensionality = samples.shape[2]

	def DrawTrainSamples(self, sample_count):
		chosen_indices = torch.randint(0, self.data_count, (sample_count,))
		offset = torch.randint(0, self.episode_length - self.horizon, (1,))
		offset = offset[0]

		samples_orig = self.samples[chosen_indices, offset:(offset + self.horizon)]
		targets_orig = self.targets[chosen_indices]

		return samples_orig, targets_orig
