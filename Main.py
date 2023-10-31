
def Main():
	actions = [ "help", "simulate", "train_diffusion", "train_value" ]

	action = actions[1]
	#action = actions[2]

	if action not in actions:
		action = actions[0]

	if action == "simulate":
		import scenarios.ScenarioSimulator as ScenarioSimulator

		simulator = ScenarioSimulator.ScenarioSimulator()
		simulator.Run()

	if action == "train_diffusion":
		import training.Academy as Academy

		Academy.TrainDiffusion()

	if action == "help":
		print("[write help message]")

Main()
