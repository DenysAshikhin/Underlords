import tensorflow as tf
print('wat')
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

import ray
from ray.rllib.agents.trainer import with_common_config
from ray.rllib.agents.ppo import PPOTrainer
from ray.tune.logger import pretty_print
from ray.rllib.env import PolicyServerInput
from environment import UnderlordEnv


DEFAULT_CONFIG = with_common_config({
    # Should use a critic as a baseline (otherwise don't use value baseline;
    # required for using GAE).
    "use_critic": True,
    # If true, use the Generalized Advantage Estimator (GAE)
    # with a value function, see https://arxiv.org/pdf/1506.02438.pdf.
    "use_gae": True,
    # The GAE (lambda) parameter.
    "lambda": 1.0,
    # Initial coefficient for KL divergence.
    "kl_coeff": 0.2,
    # Size of batches collected from each worker.
    "rollout_fragment_length": 25,
    # Number of timesteps collected for each SGD round. This defines the size
    # of each SGD epoch.
    "train_batch_size": 1000,
    # Total SGD batch size across all devices for SGD. This defines the
    # minibatch size within each epoch.
    "sgd_minibatch_size": 250,
    # Number of SGD iterations in each outer loop (i.e., number of epochs to
    # execute per train batch).
    "num_sgd_iter": 50,
    # Whether to shuffle sequences in the batch when training (recommended).
    "shuffle_sequences": True,
    # Stepsize of SGD.
    "lr": 5e-5,
    # Learning rate schedule.
    "lr_schedule": None,
    # Coefficient of the value function loss. IMPORTANT: you must tune this if
    # you set vf_share_layers=True inside your model's config.
    "vf_loss_coeff": 1.0,
    "model": {
        # Share layers for value function. If you set this to True, it's
        # important to tune vf_loss_coeff.
        "vf_share_layers": False,
        "use_lstm": True
    },
    # Coefficient of the entropy regularizer.
    "entropy_coeff": 0.0,
    # Decay schedule for the entropy regularizer.
    "entropy_coeff_schedule": None,
    # PPO clip parameter.
    "clip_param": 0.3,
    # Clip param for the value function. Note that this is sensitive to the
    # scale of the rewards. If your expected V is large, increase this.
    "vf_clip_param": 4000000.0,
    # If specified, clip the global norm of gradients by this amount.
    "grad_clip": None,
    # Target value for KL divergence.
    "kl_target": 0.01,
    # Whether to rollout "complete_episodes" or "truncate_episodes".
    "batch_mode": "truncate_episodes",
    # Which observation filter to apply to the observation.
    "observation_filter": "NoFilter",
    # Uses the sync samples optimizer instead of the multi-gpu one. This is
    # usually slower, but you might want to try it if you run into issues with
    # the default optimizer.

    "num_workers": 0,
    "framework": "tfe",
    "explore": True,
    "input": (
        lambda ioctx: PolicyServerInput(ioctx, '192.168.0.18', 55555)
    ),
    "exploration_config": {
        "type": "Curiosity",  # <- Use the Curiosity module for exploring.
        "eta": 1.0,  # Weight for intrinsic rewards before being added to extrinsic ones.
        "lr": 0.001,  # Learning rate of the curiosity (ICM) module.
        "feature_dim": 288,  # Dimensionality of the generated feature vectors.
        # Setup of the feature net (used to encode observations into feature (latent) vectors).
        "feature_net_config": {
            "fcnet_hiddens": [],
            "fcnet_activation": "relu",
        },
        "inverse_net_hiddens": [256],  # Hidden layers of the "inverse" model.
        "inverse_net_activation": "relu",  # Activation of the "inverse" model.
        "forward_net_hiddens": [256],  # Hidden layers of the "forward" model.
        "forward_net_activation": "relu",  # Activation of the "forward" model.
        "beta": 0.2,  # Weight for the "forward" loss (beta) over the "inverse" loss (1.0 - beta).
        # Specify, which exploration sub-type to use (usually, the algo's "default"
        # exploration, e.g. EpsilonGreedy for DQN, StochasticSampling for PG/SAC).
        "sub_exploration": {
            "type": "StochasticSampling",
        }
    }
})

# DEFAULT_CONFIG["num_workers"] = 1
# DEFAULT_CONFIG['env'] = UnderlordEnv
# DEFAULT_CONFIG['create_env_on_driver'] = True
# DEFAULT_CONFIG["input"] = lambda ioctx: PolicyServerInput(ioctx, '192.168.0.18', 55555)
# print(DEFAULT_CONFIG)

ray.init(local_mode=True)

trainer = PPOTrainer(config=DEFAULT_CONFIG, env=UnderlordEnv)

# Serving and training loop.
for i in range(3):
    print(pretty_print(trainer.train()))
    print(f"Finished train run #{i + 1}")