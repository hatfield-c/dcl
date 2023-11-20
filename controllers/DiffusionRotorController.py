import pybullet as pb
import torch
import numpy as np
import math

import CONFIG
import controllers.ControllerInterface as ControllerInterface

import training.Normalizer as Normalizer
import training.temporal as temporal
import training.diffusion as diffusion
import training.training as training
import training.guides as guides
import training.policies as policies

class DiffusionRotorController(ControllerInterface.ControllerInterface):
	def __init__(
			self,
			force_scale,
			torque_scale,
		):
		self.force_scale = force_scale
		self.torque_scale = torque_scale
		self.thrust_multiplier = 1

		horizon = CONFIG.horizon
		self.timesteps = CONFIG.n_timesteps
		total_size = CONFIG.total_size
		state_size = CONFIG.state_size
		action_size = CONFIG.action_size
		label_dif = CONFIG.diffusion_epochs
		label_val = CONFIG.value_epochs

		diffusion_dim_mults = CONFIG.diffusion_dim_mults
		value_dim_mults = CONFIG.value_dim_mults

		horizon = CONFIG.horizon

		total_size = CONFIG.total_size
		state_size = CONFIG.state_size
		action_size = CONFIG.action_size

		seed_path = CONFIG.seed_path
		seed_maxes_path = CONFIG.seed_maxes_path

		seed_data = torch.load(seed_path).cuda()
		#seed_maxes = torch.load(seed_maxes_path)

		self.normalizer = Normalizer.Normalizer(seed_data, action_size)
		self.normalizer.GoToCuda()

		self.temporal_model = temporal.TemporalUnet(horizon = horizon, transition_dim = total_size, cond_dim = None, dim_mults=diffusion_dim_mults, attention = True)
		self.temporal_model = self.temporal_model.cuda()

		self.diffusion_manager = diffusion.GaussianDiffusion(self.temporal_model, horizon, state_size, action_size, n_timesteps = self.timesteps, predict_epsilon = False)
		self.diffusion_manager = self.diffusion_manager.cuda()

		self.trainer = training.Trainer(
			diffusion_model = self.diffusion_manager,
			dataloader = None,
			dataset = None,
			renderer = None,
			log_freq = 10,
			save_freq = 1e20,
			sample_freq = 1e20,
			results_folder = CONFIG.diffusion_model_path
		)
		self.trainer.load(label_dif)

		self.temporal_value = temporal.ValueFunction(horizon = horizon, transition_dim = total_size, cond_dim = None, dim_mults=value_dim_mults)
		self.temporal_value = self.temporal_value.cuda()

		self.value_manager = diffusion.ValueDiffusion(
			self.temporal_value,
			horizon,
			state_size,
			action_size,
			loss_type = "value_l2",
			n_timesteps = self.timesteps,
			predict_epsilon = False
		)
		self.value_manager = self.value_manager.cuda()

		self.trainer = training.Trainer(
			diffusion_model = self.value_manager,
			dataloader = None,
			dataset = None,
			renderer = None,
			log_freq = 10,
			save_freq = 1e20,
			sample_freq = 1e20,
			results_folder = CONFIG.value_model_path
		)
		self.trainer.load(label_val)

		self.guide = guides.ValueGuide(self.value_manager, scale = 0.1)
		self.policy = policies.GuidedPolicy(self.guide, self.diffusion_manager, self.normalizer)

		self.plan = None
		self.plan_index = 0

	def GetControlSignal(self, plan, metadata):
		control_data = {}


		target_offset = plan["target_offset"]
		rotation = plan["rotation"]
		velocity = plan["velocity"]
		angular_velocity = plan["angular_velocity"]

		target_offset = torch.FloatTensor(target_offset).cuda()
		rotation = torch.FloatTensor(rotation).cuda()
		velocity = torch.FloatTensor(velocity).cuda()
		angular_velocity = torch.FloatTensor(angular_velocity).cuda()

		observation = [ target_offset, rotation, velocity, angular_velocity ]
		observation = torch.cat(observation)

		batch_size = 1

		#observation = torch.FloatTensor(observation).cuda()
		observation = observation.view(1, 1, -1)
		observation = observation.repeat(batch_size, 1, 1)

		conditions = {0: observation}

		if self.plan_index >= 1:
			self.plan = None

		if self.plan is None:
			action, samples, pred_reward = self.policy(conditions, batch_size = batch_size)

			self.plan = samples
			self.plan_index = 0

		plan_step = self.plan[self.plan_index]
		self.plan_index += 1

		action = plan_step[:5]

		control_data["fr_rotor_force"] = action[0]
		control_data["fl_rotor_force"] = action[1]
		control_data["br_rotor_force"] = action[2]
		control_data["bl_rotor_force"] = action[3]
		control_data["torque"] = action[4]
		control_data["drop_package"] = plan["drop_package"]

		return control_data
