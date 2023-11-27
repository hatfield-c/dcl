
timestep = 0.00001

client_count = 1#37
render_scenario = True#False

episode_count = 300
episode_length = 700
print_every_episode_generated = 1#0#0
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
action = "build_video"

simulation_episode_length = 700
observer_episode_length = 700

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
state_size = 9
action_size = 1
total_size = state_size + action_size
n_timesteps = 100

diffusion_epochs = 10000
value_epochs = 10000

diffusion_dim = 32
value_dim = 32

#diffusion_dim_mults = (1, 4, 8)
diffusion_dim_mults = (1, 4, 8)
#value_dim_mults = (1, 2, 4)
value_dim_mults = (1, 4, 8)

num_diffusion_norm_groups = 8
num_value_norm_groups = 8

diffusion_lr = 2e-4
value_lr = 2e-4

diffusion_batch_size = 128
value_batch_size = 128
