
import CONFIG

def Main():
	actions = [ "help", "simulate", "stitch_data", "train_diffusion", "train_value" ]

	#action = actions[1]
	#action = actions[2]
	action = actions[3]

	if action not in actions:
		action = actions[0]

	if action == "simulate":
		import scenarios.ScenarioSimulator as ScenarioSimulator

		simulator = ScenarioSimulator.ScenarioSimulator()
		simulator.Run()

	if action == "train_diffusion":
		import training.Academy as Academy

		Academy.TrainDiffusion()

	if action == "stitch_data":
		import data_processing.DataStitcher as DataStitcher

		stitcher = DataStitcher.DataStitcher()
		stitcher.StitchData(
			state_data_path = CONFIG.state_data_path,
			max_data_path = CONFIG.max_data_path,
			value_data_path = CONFIG.value_data_path,
			client_count = CONFIG.client_count,
		)

	if action == "help":
		print("[write help message]")

Main()
