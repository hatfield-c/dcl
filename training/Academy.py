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

	factory = DropScenarioFactory.DropScenarioFactory(
		gravity_strength = CONFIG.gravity_strength,
		episode_count = CONFIG.episode_count,
		episode_length = CONFIG.episode_length,
		state_data_path = CONFIG.state_data_path,
		max_data_path = CONFIG.max_data_path,
		value_data_path = CONFIG.value_data_path
	)
	client_count = CONFIG.client_count
	render_scenario = CONFIG.render_scenario
	timestep = CONFIG.timestep

	simulator = ScenarioSimulator.ScenarioSimulator(factory)
	simulator.Run(
		client_count = client_count,
		render_scenario = render_scenario,
		timestep = timestep
	)

def TrainDiffusion():

	horizon = 4
	total_size = 17
	state_size = 12
	action_size = 5
	n_timesteps = 20

	epochs = 100

	seed_path = CONFIG.seed_path
	#seed_maxes_path = CONFIG.seed_maxes_path
	value_path = CONFIG.value_path

	seed_data = torch.load(seed_path).cuda()
	#seed_maxes = torch.load(seed_maxes_path)
	seed_values = torch.load(value_path).cuda()

	#seed_maxes = torch.ones(seed_maxes.shape[0])

	normalizer = Normalizer.Normalizer(seed_data)
	#normalizer.GoToCuda()

	seed_data = normalizer.normalize(seed_data)

	data_loader = DataLoader.DataLoader(seed_data, seed_values, horizon)

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
	total_size = 17
	state_size = 12
	action_size = 5
	epochs = 100
	n_timesteps = 20

	seed_path = CONFIG.seed_path
	seed_maxes_path = CONFIG.seed_maxes_path
	value_path = CONFIG.value_path

	seed_data = torch.load(seed_path).cuda()
	seed_maxes = torch.load(seed_maxes_path)
	seed_values = torch.load(value_path).cuda()

	#seed_values = seed_values / torch.max(seed_values)
	#seed_maxes = torch.ones(seed_maxes.shape[0])

	normalizer = Normalizer.Normalizer(seed_data)

	seed_data = normalizer.normalize(seed_data)

	data_loader = DataLoader.DataLoader(seed_data, seed_values, horizon)

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

	horizon = 4
	timesteps = 20
	total_size = 23
	state_size = 17
	action_size = 6
	label_dif = 10000
	label_val = 10000

	seed_path = CONFIG.seed_path
	seed_maxes_path = CONFIG.seed_maxes_path

	seed_data = torch.load(seed_path).cuda()
	#seed_maxes = torch.load(seed_maxes_path)

	normalizer = Normalizer.Normalizer(seed_data)
	normalizer.GoToCuda()

	temporal_model = temporal.TemporalUnet(horizon = horizon, transition_dim = total_size, cond_dim = None, dim_mults=(1, 4, 8), attention = True)
	temporal_model = temporal_model.cuda()

	diffusion_manager = diffusion.GaussianDiffusion(temporal_model, horizon, state_size, action_size, n_timesteps = timesteps, predict_epsilon = False)
	diffusion_manager = diffusion_manager.cuda()

	trainer = training.Trainer(
		diffusion_model = diffusion_manager,
		dataloader = None,
		dataset = None,
		renderer = None,
		log_freq = 10,
		save_freq = 1e20,
		sample_freq = 1e20,
		results_folder = "models/diffusion/"
	)
	trainer.load(label_dif)

	temporal_value = temporal.ValueFunction(horizon = horizon, transition_dim = total_size, cond_dim = None, dim_mults=(1, 2, 4, 8))
	temporal_value = temporal_value.cuda()

	value_manager = diffusion.ValueDiffusion(temporal_value, horizon, state_size, action_size, loss_type = "value_l2", n_timesteps = timesteps, predict_epsilon = False)
	value_manager = value_manager.cuda()

	trainer = training.Trainer(
		diffusion_model = value_manager,
		dataloader = None,
		dataset = None,
		renderer = None,
		log_freq = 10,
		save_freq = 1e20,
		sample_freq = 1e20,
		results_folder = "models/value/"
	)
	trainer.load(label_val)

	guide = guides.ValueGuide(value_manager, scale = 0.1)

	planner = DiffusionPlanner.DiffusionPlanner()
	planner.Plan(diffusion_manager, guide, normalizer)
