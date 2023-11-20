
timestep = 0.00001

client_count = 37
render_scenario = False

episode_count = 4400
episode_length = 4
print_every_episode_generated = 100
pause_every_episode = False

state_data_path = "data/v2/state_data"
max_data_path = "data/v2/max_data"
value_data_path = "data/v2/value_data"

gravity_strength = 9.8

#action = "generate_data"
#action = "stitch_data"
#action = "train_diffusion"
#action = "train_value"
action = "diffusion_planning"
#action = "build_video"

simulation_episode_length = 256
observer_episode_length = 4

############################
#	DIFFUSION PARAMETERS
############################

seed_path = state_data_path + ".pt"
seed_maxes_path = max_data_path + ".pt"
value_path = value_data_path + ".pt"

diffusion_model_path = "models/diffusion/v2/"
value_model_path = "models/value/v2/"

horizon = 4
horizon_scale = 1
state_size = 12
action_size = 5
total_size = state_size + action_size
n_timesteps = 50

diffusion_epochs = 20000
value_epochs = 10000

diffusion_dim_mults = (1, 4, 8)
value_dim_mults = (1, 2, 4)

diffusion_lr = 2e-4#2e-4
value_lr = 2e-4

diffusion_batch_size = 128
value_batch_size = 128
