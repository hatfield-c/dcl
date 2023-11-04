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

class DiffusionController(ControllerInterface.ControllerInterface):
	def __init__(
			self,
			force_scale,
			torque_scale,
		):
		self.force_scale = force_scale
		self.torque_scale = torque_scale
		self.thrust_multiplier = 1

		horizon = 4
		self.timesteps = 20
		total_size = 17
		state_size = 12
		action_size = 5
		label_dif = 10000
		label_val = 10000

		seed_path = CONFIG.seed_path
		seed_maxes_path = CONFIG.seed_maxes_path

		seed_data = torch.load(seed_path).cuda()
		#seed_maxes = torch.load(seed_maxes_path)

		self.normalizer = Normalizer.Normalizer(seed_data, action_size)
		self.normalizer.GoToCuda()

		self.temporal_model = temporal.TemporalUnet(horizon = horizon, transition_dim = total_size, cond_dim = None, dim_mults=(1, 4, 8), attention = True)
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
			results_folder = "models/diffusion/"
		)
		self.trainer.load(label_dif)

		self.temporal_value = temporal.ValueFunction(horizon = horizon, transition_dim = total_size, cond_dim = None, dim_mults=(1, 2, 4, 8))
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
			results_folder = "models/value/"
		)
		self.trainer.load(label_val)

		#self.guide = guides.ValueGuide(self.value_manager, scale = 0.1)
		self.guide = guides.ValueGuide(self.value_manager, scale = 1)
		self.policy = policies.GuidedPolicy(self.guide, self.diffusion_manager, self.normalizer)

		#planner = DiffusionPlanner.DiffusionPlanner()
		#planner.Plan(diffusion_manager, guide, normalizer)

	def GetControlSignal(self, plan, metadata):
		control_signal = {}

		move_action = plan["move_action"]

		if move_action == "move":
			control_signal = self.MoveAction(plan)

		return control_signal


	def MoveAction(self, plan):
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
		action, samples, pred_reward = self.policy(conditions, batch_size = batch_size)

		arm_actuator_signal = action[0]
		thrust_rpm = action[1]
		pitch_rpm = action[2]
		roll_rpm = action[3]
		yaw_rpm = action[4]

		actuate_dropper = False
		if arm_actuator_signal > 0.5:
			actuate_dropper = True

		control_data = self.MotorMixer(thrust_rpm, yaw_rpm, pitch_rpm, roll_rpm)

		control_data["drop_package"] = actuate_dropper
		control_data["thrust_signal"] = thrust_rpm
		control_data["pitch_signal"] = pitch_rpm
		control_data["roll_signal"] = roll_rpm
		control_data["yaw_signal"] = yaw_rpm

		return control_data

	def MotorMixer(self, thrust, yaw, pitch, roll):
		motor_vals = {}

		if thrust < 0:
			thrust = self.thrust_multiplier * thrust

		fr = thrust + yaw + pitch + roll
		fl = thrust - yaw + pitch - roll
		br = thrust - yaw - pitch + roll
		bl = thrust + yaw - pitch - roll

		motor_vals["fr_rotor_force"] = fr * self.force_scale
		motor_vals["fl_rotor_force"] = fl * self.force_scale
		motor_vals["br_rotor_force"] = br * self.force_scale
		motor_vals["bl_rotor_force"] = bl * self.force_scale

		motor_vals["torque"] = yaw * self.torque_scale

		return motor_vals
