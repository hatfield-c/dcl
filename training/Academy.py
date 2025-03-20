import CONFIG

import scenarios.ScenarioSimulator as ScenarioSimulator
import scenarios.factories.DropScenarioFactory as DropScenarioFactory
import scenarios.factories.GenericScenarioFactory as GenericScenarioFactory
import scenarios.factories.HitPolyScenarioFactory as HitPolyScenarioFactory
import scenarios.factories.DroneMazeScenarioFactory as DroneMazeScenarioFactory

import training.Trainer as Trainer
import training.training as training
import training.diffusion as diffusion
import training.temporal as temporal
import training.guides as guides

import training.DataLoader as DataLoader
import training.Normalizer as Normalizer

import models.HitPolyModel as HitPolyModel
import models.NeuralGridModel as NeuralGridModel

import torch
import numpy as np

def Playground():

	import pybullet as pb

	client_count = CONFIG.client_count
	render_scenario = CONFIG.render_scenario
	timestep = CONFIG.timestep

	factory = DroneMazeScenarioFactory.DroneMazeScenarioFactory(
		gravity_strength = CONFIG.gravity_strength,
		max_episodes = 1,
		episode_length = 10000000,
	)

	simulator = ScenarioSimulator.ScenarioSimulator(factory)
	simulator.Run(
		client_count = client_count,
		render_scenario = render_scenario,
		timestep = timestep
	)

def GenerateData():

	import pybullet as pb

	client_count = CONFIG.client_count
	render_scenario = CONFIG.render_scenario
	timestep = CONFIG.timestep

	factory = HitPolyScenarioFactory.HitPolyScenarioFactory(
		gravity_strength = CONFIG.gravity_strength,
		max_episodes = CONFIG.episode_count,
		episode_length = CONFIG.episode_length,
		ai_type = "pid_align_data",
		render_poly = False,
		state_data_path = CONFIG.state_data_path,
		max_data_path = CONFIG.max_data_path,
		value_data_path = CONFIG.value_data_path,
		episode_print_count = CONFIG.print_every_episode_generated,
		render_scenario = render_scenario,
		save_render = False,
		save_data = True
	)

	simulator = ScenarioSimulator.ScenarioSimulator(factory)
	simulator.Run(
		client_count = client_count,
		render_scenario = render_scenario,
		timestep = timestep
	)

def TrainHitPoly():
	epochs = CONFIG.epochs
	learning_rate = CONFIG.learning_rate
	batch_size = CONFIG.batch_size
	dimensionality = CONFIG.dimensionality

	data_loader = DataLoader.DataLoader()

	model = None
	if(CONFIG.ai_type == "pid_align_ng"):
		model = NeuralGridModel.NeuralGridModel(dimensionality)
	else:
		model = NeuralGridModel.NeuralGridModel(dimensionality)
		
	model = model.cuda()

	trainer = Trainer.Trainer(
		model = model,
		data_loader = data_loader,
		learning_rate = learning_rate,
		batch_size = batch_size,
		print_every_epoch = CONFIG.print_every_epoch,
		save_path = CONFIG.model_path
	)

	trainer.Train(epochs)
	trainer.Save(epochs)

def RenderHitPoly():
	timestep = CONFIG.timestep

	factory = HitPolyScenarioFactory.HitPolyScenarioFactory(
		gravity_strength = CONFIG.gravity_strength,
		max_episodes = CONFIG.episode_count,
		episode_length = CONFIG.simulation_episode_length,
		ai_type = "pid_align_poly",
		render_poly = False,
		state_data_path = None,
		max_data_path = None,
		value_data_path = None,
		episode_print_count = 1,
		render_scenario = True,
		save_render = False,
		save_data = False
	)

	simulator = ScenarioSimulator.ScenarioSimulator(factory)
	simulator.Run(
		client_count = 1,
		render_scenario = True,
		timestep = timestep
	)

def TrainDiffusion():

	horizon = CONFIG.horizon
	horizon_scale = CONFIG.horizon_scale
	total_size = CONFIG.total_size
	state_size = CONFIG.state_size
	action_size = CONFIG.action_size
	n_timesteps = CONFIG.n_timesteps
	dim = CONFIG.diffusion_dim
	dim_mults = CONFIG.diffusion_dim_mults
	batch_size = CONFIG.diffusion_batch_size

	epochs = CONFIG.diffusion_epochs
	lr = CONFIG.diffusion_lr

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

	temporal_model = temporal.TemporalUnet(
		horizon = horizon,
		transition_dim = total_size,
		cond_dim = None,
		dim = dim,
		dim_mults = dim_mults,
		num_norm_groups = CONFIG.num_diffusion_norm_groups,
		attention = True
	)
	temporal_model = temporal_model.cuda()

	diffusion_manager = diffusion.GaussianDiffusion(
		temporal_model,
		horizon,
		state_size,
		action_size,
		loss_type = "l2",
		n_timesteps = n_timesteps,
		predict_epsilon = False
	)
	diffusion_manager = diffusion_manager.cuda()

	trainer = training.Trainer(
		diffusion_model = diffusion_manager,
		dataloader = data_loader,
		dataset = seed_data,
		train_lr = lr,
		renderer = None,
		log_freq = 100,
		train_batch_size = batch_size,
		gradient_accumulate_every = 2,
		save_freq = 1e20,
		sample_freq = 1e20,
		results_folder = CONFIG.diffusion_model_path
	)

	trainer.train(epochs)
	trainer.save(epochs)

def TrainValue():
	horizon = CONFIG.horizon
	horizon_scale = CONFIG.horizon_scale
	total_size = CONFIG.total_size
	state_size = CONFIG.state_size
	action_size = CONFIG.action_size
	n_timesteps = CONFIG.n_timesteps
	dim = CONFIG.value_dim
	dim_mults = CONFIG.value_dim_mults
	batch_size = CONFIG.value_batch_size

	epochs = CONFIG.value_epochs
	lr = CONFIG.value_lr

	episode_length = CONFIG.episode_length

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

	data_loader = DataLoader.DataLoader(seed_data, seed_values, episode_length, horizon, horizon_scale)

	temporal_model = temporal.ValueFunction(
		horizon = horizon,
		transition_dim = total_size,
		dim = dim,
		dim_mults = dim_mults,
		num_norm_groups = CONFIG.num_value_norm_groups,
		cond_dim = None
	)
	temporal_model = temporal_model.cuda()

	diffusion_manager = diffusion.ValueDiffusion(
		temporal_model,
		horizon,
		state_size,
		action_size,
		loss_type = "value_l2",
		n_timesteps = n_timesteps,
		predict_epsilon = False
	)
	diffusion_manager = diffusion_manager.cuda()

	trainer = training.Trainer(
		diffusion_model = diffusion_manager,
		dataloader = data_loader,
		dataset = seed_data,
		train_lr = lr,
		renderer = None,
		log_freq = 100,
		train_batch_size = batch_size,
		gradient_accumulate_every = 2,
		save_freq = 1e20,
		sample_freq = 1e20,
		results_folder = CONFIG.value_model_path
	)

	trainer.train(epochs)
	trainer.save(epochs)

def DiffusionPlanning():

	factory = DropScenarioFactory.DropScenarioFactory(
		gravity_strength = CONFIG.gravity_strength,
		max_episodes = CONFIG.episode_count,
		simulation_episode_length = CONFIG.simulation_episode_length,
		observer_episode_length = CONFIG.observer_episode_length,
		ai_type = "pid_align",
		state_data_path = None,
		max_data_path = None,
		value_data_path = None,
		episode_print_count = 50,
		render_scenario = False,
		save_render = True,
		is_saved = False
	)

	timestep = CONFIG.timestep

	simulator = ScenarioSimulator.ScenarioSimulator(factory)
	simulator.Run(
		client_count = 1,
		render_scenario = False,
		timestep = timestep
	)
