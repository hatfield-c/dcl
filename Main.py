
import time

import CONFIG
import training.Academy as Academy
import render.VideoBuilder as VideoBuilder

def Main():
	start_time = time.time()

	actions = [ "help", "generate_data", "stitch_data", "train_diffusion", "train_value", "diffusion_planning", "build_video" ]

	action = CONFIG.action

	if action not in actions:
		action = actions[0]

	if action == actions[1]:

		Academy.GenerateData()

	if action == actions[2]:
		import data_processing.DataStitcher as DataStitcher

		stitcher = DataStitcher.DataStitcher()
		stitcher.StitchData(
			state_data_path = CONFIG.state_data_path,
			max_data_path = CONFIG.max_data_path,
			value_data_path = CONFIG.value_data_path,
			client_count = CONFIG.client_count,
		)

	if action == actions[3]:

		Academy.TrainDiffusion()

	if action == actions[4]:

		Academy.TrainValue()

	if action == actions[5]:
		Academy.DiffusionPlanning()

	if action == actions[6]:
		builder = VideoBuilder.VideoBuilder()
		builder.write_video()

	if action == "help":
		print("[write help message]")

	runtime = time.time() - start_time
	runtime = "{:.2f}".format(runtime)

	print("\n[" + action + "]: Operation complete")
	print("    Total runtime: " + runtime + " sec\n")

Main()
