import torch
import math

import CONFIG
import entities.SimpleEntity as SimpleEntity

import training.Trainer as Trainer
import training.Normalizer as Normalizer
import training.DataLoader as DataLoader

import models.HitPolyModel as HitPolyModel

import planners.PlannerInterface as PlannerInterface

class HitPolyPlanner(PlannerInterface.PlannerInterface):

	def __init__(self, client_id, render_poly = False):
		self.client_id = client_id
		self.render_poly = render_poly

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

		seed_path = CONFIG.seed_path
		value_path = CONFIG.value_path

		seed_data = torch.load(seed_path).cuda()
		seed_values = torch.load(value_path).cuda()

		normalizer = Normalizer.Normalizer(seed_data, dimensionality)
		self.normalizer = normalizer
		#normalizer.GoToCuda()

		#seed_data = normalizer.normalize(seed_data)

		data_loader = DataLoader.DataLoader(seed_data, seed_values)

		model = HitPolyModel.HitPolyModel(dimensionality)
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

		self.hit_markers = []
		if self.render_poly:
			self.RenderHitPoly()

	def GetPlan(self, sensors, metadata):

		input("Press enter to continue...")

		plan = {
			"drop_package": True
		}

		return plan

	def RenderHitPoly(self):

		print("Rendering hit poly...")
		print("Collecting query points...")

		rotation = torch.FloatTensor([-math.pi / 4, 0, 0 * math.pi])
		velocity = torch.FloatTensor([0, 6, 0])
		angular_velocity = torch.FloatTensor([0, 0, 0])

		query_positions = []
		start_position = self.offset - self.render_bounds

		i_count = int(self.steps[0])
		j_count = int(self.steps[1])
		k_count = int(self.steps[2])

		total_iterations = 0

		for i in range(i_count):

			i_offset = i * self.resolution[0]

			for j in range(j_count):
				j_offset = j * self.resolution[1]

				for k in range(k_count):
					total_iterations += 1

					if total_iterations % int(self.query_count / 10) == 0:
						progress = 100 * total_iterations / self.query_count
						progress = "{:.2f}%".format(progress)
						print("   ", progress)

					k_offset = k * self.resolution[2]

					current_offset = torch.FloatTensor([i_offset, j_offset, k_offset])
					current_position = start_position + current_offset

					if abs(current_position[0]) < 1.5 and abs(current_position[1]) < 1.5:
						continue

					query = torch.cat((current_position, rotation, velocity, angular_velocity))

					query_positions.append(query)

		#query_positions.append(torch.FloatTensor([
		#	6.8895e-01,  1.2436e+00,  1.7565e+00,
		#	-7.8540e-01,  2.7756e-17, 2.6357e+00,
		#	-3.4906e+00, -6.3007e+00,  0.0000e+00,
		#	0.0000e+00, 0.0000e+00,  0.0000e+00
		#	]))

		query_positions = torch.stack(query_positions)
		query_cuda = query_positions.cuda()

		#query_cuda = self.normalizer.normalize(query_cuda)

		predictions = self.model(query_cuda)
		predictions = predictions.cpu()

		print("Instantiating hit poly markers...")

		total_iterations = 0
		for i in range(query_positions.shape[0]):
			total_iterations += 1

			if total_iterations % int(self.query_count / 10) == 0:
				progress = 100 * total_iterations / self.query_count
				progress = "{:.2f}%".format(progress)
				print("   ", progress)

			position = query_positions[i, :3]
			prediction = predictions[i]

			position = position.numpy()
			prediction = prediction.item()

			if prediction > 0.999:

				marker = SimpleEntity.SimpleEntity(
					urdf_name = "entity_files/markers/red_cube.urdf",
					client_id = self.client_id,
					position = position,
					scaling = self.scale
				)

				self.hit_markers.append(marker)
