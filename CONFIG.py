# set to 0 for data generation
#timestep = 0
timestep = 1 / 240

client_count = 1#37
render_scenario = False

episode_count = 100000
episode_length = 164
print_every_episode_generated = 500
pause_every_episode = False

state_data_path = "data/v4/state_data"
max_data_path = "data/v4/max_data"
value_data_path = "data/v4/value_data"

gravity_strength = 9.8

action = None
#action = "generate_data"
#action = "stitch_data"
#action = "train_hitpoly"
#action = "query_hitpoly"
#action = "render_hitpoly"
#action = "build_video"

possible_actions = {
	"help": "help",
	"generate_data": "generate_data",
	"stitch_data": "stitch_data",
	"build_video": "build_video",
	"train_hitpoly": "train_hitpoly",
	"query_hitpoly": "query_hitpoly",
	"render_hitpoly": "render_hitpoly",
	"extract_hitpoly": "extract_hitpoly",
	"playground": "playground"
}
possible_actions_list = list(possible_actions.keys())

simulation_episode_length = 1400
observer_episode_length = 700

############################
#	HITPOLY PARAMETERS
############################
epochs = 80000
learning_rate = 4.5e-4
dimensionality = 12
batch_size = 2048

print_every_epoch = 1000

model_path = "data/models/hitpoly/"
param_path = "data/models/hitpoly/parameters/"

############################
#	DIFFUSION PARAMETERS
############################

seed_path = state_data_path + ".pt"
seed_maxes_path = max_data_path + ".pt"
value_path = value_data_path + ".pt"

diffusion_model_path = "data/models/diffusion/v2/"
value_model_path = "data/models/value/v2/"

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
