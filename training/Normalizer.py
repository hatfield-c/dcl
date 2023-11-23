
import torch

class Normalizer:
	def __init__(self, data, action_size):
		self.action_size = action_size

		domain_low = torch.min(data, dim = 1).values
		self.domain_low = torch.min(domain_low, dim = 0).values

		domain_high = torch.max(data, dim = 1).values
		self.domain_high = torch.max(domain_high, dim = 0).values

		self.means = torch.mean(data, dim = [0, 1])
		self.std = torch.std(data, dim = [0, 1]) + 1e-20

		self.means_batch = self.means.view(1, 1, -1)
		self.std_batch = self.std.view(1, 1, -1)

	def normalize(self, data):
		data = (data - self.means_batch)
		data = data / self.std_batch

		return data

	def unnormalize(self, data):
		data = data * self.std_batch
		data = data + self.means_batch

		return data

	def NormalizeObservation(self, data):
		data = (data - self.means_batch[:, :, self.action_size:])
		data = data / self.std_batch[:, :, self.action_size:]

		return data

	def GoToCuda(self):
		self.means_batch = self.means_batch.cuda()
		self.std_batch = self.std_batch.cuda()

	def GoToCpu(self):
		self.means_batch = self.means_batch.cpu()
		self.std_batch = self.std_batch.cpu()
