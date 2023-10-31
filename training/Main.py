import sys
import Academy

if __name__ == "__main__":
	
	action = sys.argv[1]
		
	if action == "seed_data":
		Academy.SeedData()
	
	if action == "train_diffusion":
		Academy.TrainDiffusion()
		
	if action == "train_value":
		Academy.TrainValue()
		
	if action == "diffusion_planning":
		Academy.DiffusionPlanning()