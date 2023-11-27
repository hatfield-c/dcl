import pybullet as pb
import torch
import numpy as np
import math

import CONFIG
import planners.PlannerInterface as PlannerInterface
import planners.BezierAlignmentPlanner as BezierAlignmentPlanner

import training.Normalizer as Normalizer
import training.temporal as temporal
import training.diffusion as diffusion
import training.training as training
import training.guides as guides
import training.policies as policies

class DiffusionBezierAlignmentPlanner(PlannerInterface.PlannerInterface):
	def __init__(
			self,
			client_id,
			episode_length
		):
		self.client_id = client_id
		self.episode_length = episode_length

		horizon = CONFIG.horizon
		self.timesteps = CONFIG.n_timesteps
		total_size = CONFIG.total_size
		state_size = CONFIG.state_size
		action_size = CONFIG.action_size

		label_dif = CONFIG.diffusion_epochs
		label_val = CONFIG.value_epochs

		diffusion_dim_mults = CONFIG.diffusion_dim_mults
		value_dim_mults = CONFIG.value_dim_mults

		diffusion_dim = CONFIG.diffusion_dim
		value_dim = CONFIG.value_dim
		diffusion_norm_groups = CONFIG.num_diffusion_norm_groups
		value_norm_groups = CONFIG.num_value_norm_groups

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

		self.temporal_model = temporal.TemporalUnet(
			horizon = horizon,
			transition_dim = total_size,
			cond_dim = None,
			dim = diffusion_dim,
			dim_mults=diffusion_dim_mults,
			num_norm_groups = diffusion_norm_groups,
			attention = True
		)
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

		self.temporal_value = temporal.ValueFunction(
			horizon = horizon,
			transition_dim = total_size,
			cond_dim = None,
			dim = value_dim,
			dim_mults=value_dim_mults,
			num_norm_groups = value_norm_groups,
		)
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

		self.guide = guides.ValueGuide(self.value_manager, scale = 1000)
		self.policy = policies.GuidedPolicy(self.guide, self.diffusion_manager, self.normalizer)

		self.plan = None
		self.bezier_planner = BezierAlignmentPlanner.BezierAlignmentPlanner(self.client_id, control_points = np.zeros((4, 3)), episode_length = self.episode_length, debug = True)

		self.interpolation = 0
		self.alignment = 1
		self.step_size = 1 / self.episode_length

	def GetPlan(self, sensors, metadata):
		telemetry = sensors["telemetry"]
		sensor_data = telemetry.ReadSensor(None)

		current_position = sensor_data["position"]
		velocity = sensor_data["velocity"]
		current_quat = sensor_data["quaternion"]

		rotation = sensor_data["rotation"]
		angular_velocity = sensor_data["angular_velocity"]

		current_position_torch = torch.FloatTensor(current_position).cuda()
		rotation_torch = torch.FloatTensor(rotation).cuda()
		velocity_torch = torch.FloatTensor(velocity).cuda()
		angular_velocity_torch = torch.FloatTensor(angular_velocity).cuda()

		velocity_magnitude = np.linalg.norm(velocity)

		if self.interpolation == 0:
			if velocity[0] > 0 or (velocity_magnitude == 0 and current_position[0] > 0):
				self.alignment = -1

		if self.plan is None:
			observation = [ current_position_torch[[0]], rotation_torch, velocity_torch[[0, 1]], angular_velocity_torch ]
			observation = torch.cat(observation)

			batch_size = 1

			#observation = torch.FloatTensor(observation).cuda()
			observation = observation.view(1, 1, -1)
			observation = observation.repeat(batch_size, 1, 1)

			conditions = {0: observation}

			action, samples, pred_reward = self.policy(conditions, batch_size = batch_size)

			action_size = self.diffusion_manager.action_dim
			control_points = self.alignment * samples[:, :action_size]

			one_fives = np.ones(control_points.shape) * 1.5
			y_vals = np.array([[0], [3.33], [6.66], [10]])

			control_points = np.concatenate((control_points, y_vals, one_fives), axis = 1)

			print(control_points)

			self.bezier_planner.SetNewPath(control_points)
			self.plan = control_points

		bezier_plan = self.bezier_planner.GetPlan(sensors, metadata)

		drop_package = False

		plan = {
			"move_action": "move",
			"current_quat": current_quat,
			"current_altitude": current_position[2],
			"desired_direction": bezier_plan["desired_direction"],
			"desired_altitude": bezier_plan["desired_altitude"],
			"velocity": velocity,
			"drop_package": drop_package
		}

		self.interpolation += self.step_size

		if self.interpolation >= 1:
			self.interpolation = 0
			self.plan = None

		return plan

	def SetNewPath(self, external_path):
		#self.plan = None
		pass
