
import time

import CONFIG
import training.Academy as Academy
import render.VideoBuilder as VideoBuilder
import hitpoly.PolyAnalysis as PolyAnalysis

def Main():
	start_time = time.time()

	actions = {
		"help": "help",
		"generate_data": "generate_data",
		"stitch_data": "stitch_data",
		"build_video": "build_video",
		"train_hitpoly": "train_hitpoly",
		"query_hitpoly": "query_hitpoly",
		"render_hitpoly": "render_hitpoly"
	}

	action = CONFIG.action

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
