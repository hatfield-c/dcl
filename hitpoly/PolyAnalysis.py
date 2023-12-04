import math
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import cv2
import torch
import numpy as np

import CONFIG
import hitpoly.HitPolyQuery as HitPolyQuery

import training.DataLoader as DataLoader
import training.Trainer as Trainer
import models.HitPolyModel as HitPolyModel

def QueryPolySpace():
	#dimensionalities = torch.FloatTensor([3, 3, 3, 3])

	#render_indices = [0, 1]
	render_indices = [6, 7]

	# [position:3, rotation:3, velocity:3, angular_velocity:3]
	#sample_steps = torch.FloatTensor([3, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1])

	# position shifting, stable velocity
	#sample_steps = np.array([256, 256, 20, 1, 1, 1, 1, 1, 1, 1, 1, 1])
	#sample_steps = np.array([75, 75, 10, 1, 1, 1, 1, 1, 1, 1, 1, 1])
	#lower_bounds = torch.FloatTensor([-4, -4, 0.5, -math.pi / 4, 0, math.pi, 0, -6, 0, 0, 0, 0])
	#upper_bounds = torch.FloatTensor([4, 4, 3.5, -math.pi / 4, 0, math.pi, 0, -6, 0, 0, 0, 0])

	# velocity shifting, stable position

	sample_steps = np.array([
		1, 1, 1,
		1, 1, 1,
		128, 128, 1,
		1, 1, 1
	])
	lower_bounds = torch.FloatTensor([
		0, -2, 2.5,
		-math.pi / 4, 0, 0,
		-4, -1, 0,
		0, 0, 0
	])
	upper_bounds = torch.FloatTensor([
		0, -2, 2.5,
		-math.pi / 4, 0, 0,
		4, 7, 0,
		0, 0, 0
	])


	dimensionality = sample_steps.shape[0]

	widths = upper_bounds - lower_bounds
	step_sizes = widths / sample_steps

	epochs = CONFIG.epochs
	learning_rate = CONFIG.learning_rate
	batch_size = CONFIG.diffusion_batch_size
	dimensionality = CONFIG.dimensionality

	seed_path = CONFIG.seed_path
	value_path = CONFIG.value_path

	seed_data = torch.load(seed_path).cuda()
	seed_values = torch.load(value_path).cuda()

	#normalizer = Normalizer.Normalizer(seed_data, dimensionality)
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

	frame_vals = np.linspace(-0.5, -3, num = 60)
	frames = frame_vals.shape[0]

	for f in range(frames):

		val = frame_vals[f]
		lower_bounds[1] = val
		upper_bounds[1] = val

		grid_positions = []
		for i in range(dimensionality):
			lower = lower_bounds[i]
			upper = upper_bounds[i]
			step_count = sample_steps[i]

			dimension_positions = None
			if step_count == 1:
				dimension_positions = torch.ones(1) * lower_bounds[i]
			else:
				dimension_positions = torch.linspace(lower, upper, int(step_count.item()))

			grid_positions.append(dimension_positions)

		grid = torch.meshgrid(*grid_positions, indexing = "ij")
		grid = torch.vstack(grid).reshape(dimensionality, -1).T

		#grid = torch.FloatTensor([[
		#	0, -2, 2,
		#	-math.pi / 4, 0, 0,
		#	0, 6, 0,
		#	0, 0, 0
		#]])

		grid = grid.cuda()

		predictions = model(grid)
		predictions = predictions.cpu()

		index_x = render_indices[0]
		index_y = render_indices[1]

		hit_field_img = np.ones((256, 256, 3)) * 255
		field_height = hit_field_img.shape[0]
		field_width = hit_field_img.shape[1]

		for i in range(predictions.shape[0]):

			if i % int(predictions.shape[0] / 20) == 0:
				progress = 100 * (i / predictions.shape[0])
				progress = "{:0.1f}%".format(progress)
				print(progress)

			position = grid[i]
			prediction = predictions[i]

			position_x = position[index_x]
			position_y = position[index_y]

			width_x = widths[index_x]
			width_y = widths[index_y]
			#print(prediction, position)
			if width_x == 0 or width_y == 0:
				continue

			#if abs(position_x) < 1 and abs(position_y) < 1:
			#	continue

			pixel_x = ((position_x - lower_bounds[index_x]) / width_x) * (field_width - 1)
			pixel_y = ((position_y - lower_bounds[index_y]) / width_y) * (field_height - 1)

			pixel_y = (field_height - 1) - pixel_y

			pixel_x = int(pixel_x)
			pixel_y = int(pixel_y)

			if prediction.item() > 0.9:
				#hit_field_img[pixel_y, pixel_x, 0] = 255
				#hit_field_img[pixel_y, pixel_x, 1] = 0
				#hit_field_img[pixel_y, pixel_x, 2] = 0

				cv2.circle(hit_field_img, (pixel_x, pixel_y), 9, (255, 0, 0), -1)

		imgplot = plt.imshow(hit_field_img, extent = [lower_bounds[index_x], upper_bounds[index_x], lower_bounds[index_y], upper_bounds[index_y]])
		plt.title("Target center at <0, 0, 1.5> Drone facing direction <0, 1, 0>\nDrone position <0, " + "{:.2f}".format(val) + ", 2.5>")
		plt.xlabel("Velocity X")
		plt.ylabel("Velocity Y")
		#plt.show()

		path = "data/render/frames/f" + str(f).zfill(4) + ".png"
		#cv2.imwrite(path, hit_field_img)
		plt.savefig(path)
		plt.cla()
		plt.clf()
