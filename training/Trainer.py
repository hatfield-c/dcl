import time
import math

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class Trainer:
	def __init__(
			self,
			model,
			data_loader,
			learning_rate,
			batch_size,
			print_every_epoch,
			save_path
		):

		self.model = model
		self.data_loader = data_loader
		self.learning_rate = learning_rate
		self.batch_size = batch_size
		self.print_every_epoch = print_every_epoch
		self.save_path = save_path

	def Train(self, epochs):

		model = self.model
		data_loader = self.data_loader
		learning_rate = self.learning_rate
		batch_size = self.batch_size
		loss_func = torch.nn.BCELoss()

		optimizer = optim.Adam(
			model.parameters(),
			lr = learning_rate
		)

		avg_time = 1
		start_total = time.time()

		for e in range(epochs):

			start_time = time.time()

			batch_data, batch_targets = data_loader.DrawSamples(batch_size)

			predictions = model(batch_data)
			loss = loss_func(predictions, batch_targets)
			optimizer.zero_grad()
			loss.backward()
			optimizer.step()

			self.PrintUpdate(epochs, e, avg_time, loss)

			avg_time = (avg_time + (time.time() - start_time)) / 2

		print("\nCompleted in", int((time.time() - start_total) / 60), "minutes.")
		print("Final loss:", loss.item())

		return model

	def PrintUpdate(self, epochs, e, avg_time, loss):

		remaining_epochs = epochs - e

		if self.ShouldPrint_E(epochs, e):
			eta = avg_time * remaining_epochs
			eta = eta / 60
			eta = "{:.2f}".format(eta)

			completion = str(100 *(e / (epochs)))
			completion = completion[:4] + "%"

			print("   [", e, "/", epochs, ":", completion,  "]")
			print("    Loss	 :", loss.item())
			print("")
			print("    Batches left :", remaining_epochs)
			print("    Avg. Time    :", "{:.2f}".format(avg_time), "s")
			print("    ETA	      :", eta, "mins")
			print("\n")

	def ShouldPrint_E(self, epochs, e):
		if epochs < self.print_every_epoch:
			return True

		return e % self.print_every_epoch == 0 or e == epochs - 1

	def Save(self, epoch):

		filename = "hitpoly_" + str(epoch) + ".pt"
		save_path = self.save_path + filename

		torch.save(self.model.state_dict(), save_path)

		print("\nSaved model to", save_path)

	def Load(self, epoch):
		filename = "hitpoly_" + str(epoch) + ".pt"
		save_path = self.save_path + filename

		self.model.load_state_dict(torch.load(save_path))
		self.model.eval()

		print("\nLoaded model from", save_path)
