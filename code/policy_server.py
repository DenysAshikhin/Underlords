# Adds the following updates to the `PPOTrainer` config in
# rllib/agents/ppo/ppo.py.
import os

import ray
from ray.rllib.agents import with_common_config
from ray.rllib.agents.impala import impala
from ray.rllib.agents.ppo import ppo, DDPPOTrainer, APPOTrainer
from ray.rllib.agents.ppo import PPOTrainer
from ray.rllib.env import PolicyServerInput
from ray.rllib.examples.custom_metrics_and_callbacks import MyCallbacks
from ray.tune.logger import pretty_print

from environment import UnderlordEnv


from ray.rllib.examples.env.random_env import RandomEnv
from gym import spaces

import argparse

parser = argparse.ArgumentParser(description='Optional app description')
parser.add_argument('-ip', type=str, help='IP of this device')

parser.add_argument('-checkpoint', type=str, help='location of checkpoint to restore from')

args = parser.parse_args()

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
    "train_batch_size": 3000,
    # Total SGD batch size across all devices for SGD. This defines the
    # minibatch size within each epoch.
    "sgd_minibatch_size": 375,
    # Number of SGD iterations in each outer loop (i.e., number of epochs to
    # execute per train batch).
    "num_sgd_iter": 60,
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
    # # the default optimizer.
    # "simple_optimizer": False,
    # Whether to fake GPUs (using CPUs).
    # Set this to True for debugging on non-GPU machines (set `num_gpus` > 0).
    # "_fake_gpus": True,
    "num_gpus": 1,
    # Use the connector server to generate experiences.
    "input": (
        lambda ioctx: PolicyServerInput(ioctx, args.ip, 55555)
    ),
    # Use a single worker process to run the server.
    "num_workers": 0,
    # Disable OPE, since the rollouts are coming from online clients.
    "input_evaluation": [],
    # "callbacks": MyCallbacks,
    "env_config": {"sleep": True, "framework": 'tf'},
    "framework": "tf",
    # "eager_tracing": True,
    "explore": True,
    "exploration_config": {
        "type": "Curiosity",  # <- Use the Curiosity module for exploring.
        "eta": 1.0,  # Weight for intrinsic rewards before being added to extrinsic ones.
        "lr": 0.001,  # Learning rate of the curiosity (ICM) module.
        "feature_dim": 576,  # Dimensionality of the generated feature vectors.
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
    },
    "create_env_on_driver": False

})

ray.init()

print(f"running on: {args.ip}:44444")

# trainer = DDPPOTrainer(config=DEFAULT_CONFIG)
trainer = PPOTrainer(config=DEFAULT_CONFIG, env=UnderlordEnv)
# trainer = APPOTrainer(config=DEFAULT_CONFIG, env=UnderlordEnv)

# checkpoint_path = CHECKPOINT_FILE.format(args.run)
checkpoint_path = "checkpointsE2/"

if args.checkpoint:
    # Attempt to restore from checkpoint, if possible.
    if os.path.exists(args.checkpoint):
        print('path FOUND!')
        print("Restoring from checkpoint path", args.checkpoint)
        trainer.restore(args.checkpoint)
    else:
        print("That path does not exist!")

# Serving and training loop.
i = 0
while True:
    print(pretty_print(trainer.train()))
    print(f"Finished train run #{i + 1}")
    i += 1
    checkpoint = trainer.save(checkpoint_path)
    print("Last checkpoint", checkpoint)

    # temp = (0, 73, 1, 5, 9, 9, 0, 0, [57, 1], 0, 2, 0, 13, [59, 24, 28, 2, 50],
    #         [50, 2, 1, 2, 0, 1, 0, 1], [49, 12, 1, 2, 0, 2, 0, 1], [3, 15, 1, 1, 0, 3, 0, 1],
    #         [47, 11, 1, 1, 0, 4, 0, 1],
    #         [45, 16, 1, 1, 0, 5, 0, 1], [30, 1, 1, 1, 0, 6, 0, 1], [39, 9, 1, 2, 0, 7, 0, 1],
    #         [15, 17, 1, 1, 0, 8, 0, 1],
    #
    #
    #
    #         [11, 13, 1, 1, 1, 2, 3, 1], [59, 4, 1, 1, 0, 2, 5, 1], [15, 3, 1, 1, 0, 3, 7, 1],
    #         [57, 14, 1, 1, 0, 3, 8, 1],            [5, 5, 2, 1, 0, 4, 7, 1],            [0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 0, 0],
    #
    #
    #         [0, 0, 0, 0, 0, 0, 0, 0],
    #         [53, 2, 0, 1, 1], [43, 3, 0, 1, 2], [23, 1, 13, 1, 1],
    #         [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
    #         [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0],
    #         [0, 0, 0],
    #         [2, 87, 21, 5, 20, 1, 18, 1, 5, 1, 23, 1, 48, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [3, 82, 32, 5, 15, 1, 5, 1, 59, 1, 20, 1, 9, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [4, 98, 31, 6, 34, 1, 49, 1, 47, 1, 16, 1, 8, 1, 55, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [5, 96, 28, 6, 22, 1, 42, 1, 24, 1, 49, 1, 48, 1, 23, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [6, 85, 33, 5, 28, 1, 18, 1, 3, 1, 40, 1, 8, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [7, 100, 32, 6, 49, 1, 34, 1, 5, 1, 34, 1, 40, 1, 29, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    #         [8, 96, 30, 6, 15, 1, 59, 1, 18, 1, 6, 1, 35, 1, 62, 1, 0, 0, 0, 0, 0, 0, 0, 0])
