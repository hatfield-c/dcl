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
		print("    [Error]: You need to specify an action with the --action argument, i.e. --action 'help' or --action 'generate_data'")
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

	if action == "help":
		print("[write help message]")

	runtime = time.time() - start_time
	runtime = "{:.2f}".format(runtime)

	print("\n[" + action + "]: Operation complete")
	print("    Total runtime: " + runtime + " sec\n")

Main()
