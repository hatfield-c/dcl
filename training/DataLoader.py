import time
import torch
import numpy as np

import CONFIG

class DataLoader:
	def __init__(self):
		state_raw = np.fromfile(CONFIG.state_data_path, np.float32)
		value_raw = np.fromfile(CONFIG.value_data_path, np.float32)
		
		state_raw = state_raw.reshape(-1, 6)
		value_raw = value_raw.reshape(-1, 1)
		
		self.samples = torch.FloatTensor(state_raw)
		self.targets = torch.FloatTensor(value_raw)
		
		self.samples = self.samples.cuda()
		self.targets = self.targets.cuda()

		print("[Samples Shape]:", self.samples.shape)

		self.data_count = self.samples.shape[0]
		self.dimensionality = self.samples.shape[1]

	def DrawSamples(self, sample_count):
		chosen_indices = torch.randint(0, self.data_count, (sample_count,))

		samples_orig = self.samples[chosen_indices]
		targets_orig = self.targets[chosen_indices]

		if(CONFIG.ai_type == "pid_align_ngn"):
			sample_noise = torch.rand(samples_orig.shape).cuda()
			sample_noise = (2 * sample_noise) - 1
			sample_noise = 0.5 * sample_noise
			
			samples_orig += sample_noise

		return samples_orig, targets_orig

