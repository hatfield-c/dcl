from collections import namedtuple
import torch
import einops
import pdb

import training.functions as functions


Trajectories = namedtuple('Trajectories', 'actions observations values')


class GuidedPolicy:

	def __init__(self, guide, diffusion_model, normalizer):
		self.guide = guide
		self.diffusion_model = diffusion_model
		self.normalizer = normalizer
		self.action_dim = diffusion_model.action_dim
		self.observation_dim = diffusion_model.observation_dim

	def __call__(self, conditions, batch_size = 1):
		for t in conditions:
			cond = conditions[t]

			cond = self.normalizer.NormalizeObservation(cond)
			cond = cond[:, 0, :]
			conditions[t] = cond

		## run reverse diffusion process
		samples = self.diffusion_model(conditions, guide = self.guide, sample_func = functions.n_step_guided_p_sample)

		values = samples.values

		#maxes, indices = torch.max(values, dim = 0)
		#max_index = indices[0]
		max_index = 0
		max_val = values[0].detach().cpu().numpy()
		#max_val = maxes[0].detach().cpu()

		trajectories = samples.trajectories[:, [0]]

		#trajectories = self.normalizer.unnormalize(trajectories)
		trajectories = trajectories.detach().cpu().numpy()

		## extract action [ batch_size x horizon x transition_dim ]
		action = trajectories[max_index, 0, :self.action_dim]

		### extract first action
		#action = actions[0, 0]

		observations = trajectories[:, :, self.action_dim:]

		trajectories = Trajectories(action, observations, samples.values)
		return action, trajectories, max_val

	@property
	def device(self):
		parameters = list(self.diffusion_model.parameters())
		return parameters[0].device
