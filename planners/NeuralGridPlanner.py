import numpy as np
import torch
import math

import CONFIG
import planners.PlannerInterface as PlannerInterface
import models.NeuralGridModel as NeuralGridModel
import training.DataLoader as DataLoader
import training.Trainer as Trainer

class NeuralGridPlanner(PlannerInterface.PlannerInterface):

	def __init__(self, client_id):
		self.client_id = client_id
	
		self.render_bounds = torch.FloatTensor([4, 4, 1.5])
		self.steps = torch.FloatTensor([30, 30, 15])
	
		chunks = self.steps - 1
		self.resolution = torch.FloatTensor([
			 2 * self.render_bounds[0] / chunks[0],
			 2 * self.render_bounds[1] / chunks[1],
			 2 * self.render_bounds[2] / chunks[2],
		])
		self.offset = torch.FloatTensor([0, 0, 2])
		#self.offset = torch.FloatTensor([0, -2, 2])
		self.scale = 0.2
	
		query_count = torch.prod(self.steps)
		self.query_count = int(query_count.item())
	
		epochs = CONFIG.epochs
		learning_rate = CONFIG.learning_rate
		batch_size = CONFIG.diffusion_batch_size
		dimensionality = CONFIG.dimensionality
	
		data_loader = DataLoader.DataLoader()
	
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
	
		trainer.Load(epochs)
	
		self.model = model

	
	def GetPlan(self, sensors, metadata):
		telemetry = sensors["telemetry"]
		sensor_data = telemetry.ReadSensor(None)
		
		position = sensor_data["position"].copy()
		rotation = sensor_data["rotation"]
		velocity = sensor_data["velocity"].copy()
		angular_velocity = sensor_data["angular_velocity"]
		
		position = position[[0, 2, 1]]
		velocity = velocity[[0, 2, 1]]		
		
		if(CONFIG.ai_type == "pid_align_ng"):
			position = position.round()
			velocity = velocity.round()
		
		state_data = [
			position,
			#rotation,
			velocity,
			#angular_velocity
		]
	
		state_data = np.concatenate(state_data).reshape((1, -1))
		state_data = torch.FloatTensor(state_data).cuda()
		
		predictions = self.model(state_data)
		predictions = predictions.cpu()
		
		threshold = 0.999
		if CONFIG.ai_type == "pid_align_ngn":
			threshold = 0.9
		
		is_drop = False
		if predictions[0, 0] > threshold:
			is_drop = True
		
		plan = {
			"is_dropped": is_drop
		}
	
		return plan
