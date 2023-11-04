import CONFIG

import scenarios.ScenarioSimulator as ScenarioSimulator
import scenarios.factories.DropScenarioFactory as DropScenarioFactory
import scenarios.factories.GenericScenarioFactory as GenericScenarioFactory
import scenarios.TeleopScenario as TeleopScenario

import training.training as training
import training.diffusion as diffusion
import training.temporal as temporal
import training.guides as guides

import training.DataLoader as DataLoader
import training.DiffusionPlanner as DiffusionPlanner
import training.Normalizer as Normalizer

import torch
import numpy as np

def GenerateData():
	#factory = GenericScenarioFactory.GenericScenarioFactory(scenario_class = TeleopScenario.TeleopScenario)
	#client_count = 1
	#render_scenario = True
	#timestep = CONFIG.timestep

	client_count = CONFIG.client_count
	render_scenario = CONFIG.render_scenario
	timestep = CONFIG.timestep

	factory = DropScenarioFactory.DropScenarioFactory(
		gravity_strength = CONFIG.gravity_strength,
		max_episodes = CONFIG.episode_count,
		episode_length = CONFIG.episode_length,
		ai_type = "waypoint",
		state_data_path = CONFIG.state_data_path,
		max_data_path = CONFIG.max_data_path,
		value_data_path = CONFIG.value_data_path,
		render_scenario = render_scenario,
		save_render = False
	)

	simulator = ScenarioSimulator.ScenarioSimulator(factory)
	simulator.Run(
		client_count = client_count,
		render_scenario = render_scenario,
		timestep = timestep
	)

def TrainDiffusion():

	horizon = 4
	horizon_scale = 20
	total_size = 18
	state_size = 12
	action_size = 6
	n_timesteps = 20

	epochs = 10000

	episode_length = CONFIG.episode_length

	seed_path = CONFIG.seed_path
	#seed_maxes_path = CONFIG.seed_maxes_path
	value_path = CONFIG.value_path

	seed_data = torch.load(seed_path).cuda()
	#seed_maxes = torch.load(seed_maxes_path)
	seed_values = torch.load(value_path).cuda()

	#seed_maxes = torch.ones(seed_maxes.shape[0])

	normalizer = Normalizer.Normalizer(seed_data, action_size)
	#normalizer.GoToCuda()

	seed_data = normalizer.normalize(seed_data)

	data_loader = DataLoader.DataLoader(seed_data, seed_values, episode_length, horizon, horizon_scale)

	temporal_model = temporal.TemporalUnet(horizon = horizon, transition_dim = total_size, cond_dim = None, dim_mults=(1, 4, 8), attention = True)
	temporal_model = temporal_model.cuda()

	diffusion_manager = diffusion.GaussianDiffusion(temporal_model, horizon, state_size, action_size, loss_type = "l2", n_timesteps = n_timesteps, predict_epsilon = False)
	diffusion_manager = diffusion_manager.cuda()

	trainer = training.Trainer(
		diffusion_model = diffusion_manager,
		dataloader = data_loader,
		dataset = seed_data,
		train_lr = 2e-4,
		renderer = None,
		log_freq = 100,
		train_batch_size = 128,
		gradient_accumulate_every = 2,
		save_freq = 1e20,
		sample_freq = 1e20,
		results_folder = "models/diffusion/"
	)

	trainer.train(epochs)
	trainer.save(epochs)

def TrainValue():

	horizon = 4
	horizon_scale = 20
	total_size = 18
	state_size = 12
	action_size = 6
	epochs = 10000
	n_timesteps = 20

	seed_path = CONFIG.seed_path
	seed_maxes_path = CONFIG.seed_maxes_path
	value_path = CONFIG.value_path

	seed_data = torch.load(seed_path).cuda()
	seed_maxes = torch.load(seed_maxes_path)
	seed_values = torch.load(value_path).cuda()

	#seed_values = seed_values / torch.max(seed_values)
	#seed_maxes = torch.ones(seed_maxes.shape[0])

	normalizer = Normalizer.Normalizer(seed_data, action_size)

	seed_data = normalizer.normalize(seed_data)

	data_loader = DataLoader.DataLoader(seed_data, seed_values, horizon, horizon_scale)

	temporal_model = temporal.ValueFunction(horizon = horizon, transition_dim = total_size, cond_dim = None)
	temporal_model = temporal_model.cuda()

	diffusion_manager = diffusion.ValueDiffusion(temporal_model, horizon, state_size, action_size, loss_type = "value_l2", n_timesteps = n_timesteps, predict_epsilon = False)
	diffusion_manager = diffusion_manager.cuda()

	trainer = training.Trainer(
		diffusion_model = diffusion_manager,
		dataloader = data_loader,
		dataset = seed_data,
		train_lr = 2e-4,
		renderer = None,
		log_freq = 100,
		train_batch_size = 128,
		gradient_accumulate_every = 2,
		save_freq = 1e20,
		sample_freq = 1e20,
		results_folder = "models/value/"
	)

	trainer.train(epochs)
	trainer.save(epochs)

def DiffusionPlanning():

	factory = DropScenarioFactory.DropScenarioFactory(
		gravity_strength = CONFIG.gravity_strength,
		max_episodes = CONFIG.episode_count,
		episode_length = CONFIG.episode_length,
		ai_type = "diffusion",
		state_data_path = None,
		max_data_path = None,
		value_data_path = None,
		render_scenario = False,
		save_render = True
	)

	timestep = CONFIG.timestep

	simulator = ScenarioSimulator.ScenarioSimulator(factory)
	simulator.Run(
		client_count = 1,
		render_scenario = False,
		timestep = timestep
	)
