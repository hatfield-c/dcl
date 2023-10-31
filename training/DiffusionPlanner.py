import torch
import time
import gymnasium
import cv2

import training.policies as policies

class DiffusionPlanner:
	def __init__(self, renderer = None):
		self.renderer = renderer

		self.state_size = 17
		self.action_size = 6
		self.dimensionality = 23

	def Plan(self, diffusion_model, guide, normalizer):

		batch_size = 32

		env = gymnasium.make(
			 'HalfCheetah-v4',
			  #render_mode = "human"
			  render_mode = "rgb_array",
			  width = 128,
			  height = 128
		)
		observation, info = env.reset()

		policy = policies.GuidedPolicy(guide, diffusion_model, normalizer)

		total_reward = 0
		for t in range(1000):

			## format current observation for conditioning
			observation = torch.FloatTensor(observation).cuda()
			observation = observation.view(1, 1, -1)
			observation = observation.repeat(batch_size, 1, 1)

			conditions = {0: observation}
			action, samples, pred_reward = policy(conditions, batch_size = batch_size)

			img = env.render()

			filename = "renders/f" + str(t) + ".png"
			cv2.imwrite(filename, img)

			## execute action in environment
			next_observation, reward, terminal, truncated, info = env.step(action)

			## print reward and score
			total_reward += reward
			#score = env.get_normalized_score(total_reward)
			print("step reward:", reward, "pred reward:", pred_reward, "total reward:", total_reward)
			#print(
			#	f't: {t} | r: {reward:.2f} |  R: {total_reward:.2f} | score: {score:.4f} | '
			#	f'values: {samples.values}',
			#	flush=True,
			#)

			if terminal:
				break

			observation = next_observation

		env.close()

	def UnStitch(self, step):
		states = step[:, :17, :]
		actions = step[:, 17:23, :]

		return states, actions
