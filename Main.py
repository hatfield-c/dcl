
import CONFIG
import training.Academy as Academy

def Main():
	actions = [ "help", "generate_data", "stitch_data", "train_diffusion", "train_value", "diffusion_planning" ]

	action = actions[1]
	#action = actions[2]
	#action = actions[3]
	#action = actions[4]
	#action = actions[5]

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
		import scenarios.ScenarioSimulator as ScenarioSimulator

		simulator = ScenarioSimulator.ScenarioSimulator()
		simulator.Run(CONFIG.client_count)

	if action == "help":
		print("[write help message]")

Main()
