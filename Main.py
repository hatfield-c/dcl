import argparse
import time

import CONFIG
import training.Academy as Academy
import render.VideoBuilder as VideoBuilder
import hitpoly.PolyAnalysis as PolyAnalysis

def GetCliAction():
	print("")
	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument("-a", "--action", type = str, help = "what action to take. Must be one of the following: " + str(CONFIG.possible_actions_list))

	args = arg_parser.parse_args()

	action = args.action

	if action is None:
		print("	[Error]: You need to specify an action with the --action argument, i.e. --action [flag].") 
		print("	For more information, try: --action help")
		exit()

	return action

def Main():
	start_time = time.time()

	actions = CONFIG.possible_actions
	action = GetCliAction()

	if action not in actions:
		action = actions["help"]

	if action == actions["generate_data"]:

		Academy.GenerateData()

	if action == actions["stitch_data"]:
		import data_processing.DataStitcher as DataStitcher

		stitcher = DataStitcher.DataStitcher()
		stitcher.StitchData(
			state_data_path = CONFIG.state_data_path,
			max_data_path = CONFIG.max_data_path,
			value_data_path = CONFIG.value_data_path,
			client_count = CONFIG.client_count,
		)

	if action == actions["build_video"]:
		builder = VideoBuilder.VideoBuilder()
		builder.write_video()

	if action == actions["train_hitpoly"]:
		Academy.TrainHitPoly()

	if action == actions["render_hitpoly"]:
		Academy.RenderHitPoly()

	if action == actions["query_hitpoly"]:
		PolyAnalysis.QueryPolySpace()

	if action == actions["extract_hitpoly"]:
		PolyAnalysis.ExtractHitpoly()

	if action == actions["test_hitpoly"]:
		PolyAnalysis.TestHitpoly()()

	if action == actions["playground"]:
		Academy.Playground()

	if action == "help":
		print("	[DCL] Drone Calibration Lab")
		print("	The DCL is built on top of the PyBullet engine and serves to simulate and calibrate AI drone controllers.")

		print("	Usage:")
		print("		python Main.py --action [OPTIONS]")
		print("		python Main.py -a [OPTIONS]")

		print("	Options:")
		print("		help			Show this screen.")
		print("		build_video		Creates an .mp4 video visualizing the change in hitpoly for ")
		print("					the drone based on its position and direction.")
		print("		generate_data		Generates initial data for training.")
		print("		stitch_data		Stitches together tensors generated from generate_data.")
		print("		train_hitpoly		Trains the hitpoly model.")
		print("		query_hitpoly		Loads the model output to be rendered into images.")
		print("		render_hitpoly		Generates the hitpoly simulator starting from episode 1.")
		print("					Hold the enter key to progress each frame.")



	runtime = time.time() - start_time
	runtime = "{:.2f}".format(runtime)

	print("\n[" + action + "]: Operation complete")
	print("    Total runtime: " + runtime + " sec\n")

Main()
