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
    "train_batch_size": 4000,
    # Total SGD batch size across all devices for SGD. This defines the
    # minibatch size within each epoch.
    "sgd_minibatch_size": 500,
    # Number of SGD iterations in each outer loop (i.e., number of epochs to
    # execute per train batch).
    "num_sgd_iter": 75,
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
    # "num_gpus": 1,
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
    "framework": "tfe",
    "eager_tracing": True,
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


# DEFAULT_CONFIG = impala.ImpalaTrainer.merge_trainer_configs(
#     impala.DEFAULT_CONFIG,  # See keys in impala.py, which are also supported.
#     {
#         # Whether to use V-trace weighted advantages. If false, PPO GAE
#         # advantages will be used instead.
#         "vtrace": True,
#
#         # == These two options only apply if vtrace: False ==
#         # Should use a critic as a baseline (otherwise don't use value
#         # baseline; required for using GAE).
#         "use_critic": True,
#         # If true, use the Generalized Advantage Estimator (GAE)
#         # with a value function, see https://arxiv.org/pdf/1506.02438.pdf.
#         "use_gae": True,
#         # GAE(lambda) parameter
#         "lambda": 1.0,
#
#         # == PPO surrogate loss options ==
#         "clip_param": 40000000,
#
#         # == PPO KL Loss options ==
#         "use_kl_loss": False,
#         "kl_coeff": 1.0,
#         "kl_target": 0.01,
#
#         # == IMPALA optimizer params (see documentation in impala.py) ==
#         "rollout_fragment_length": 25,
#         "train_batch_size": 4000,
#         "min_iter_time_s": 10,
#         "num_workers": 0,
#         "num_gpus": 0,
#         "num_data_loader_buffers": 1,
#         "minibatch_buffer_size": 1,
#         "num_sgd_iter": 60,
#         "replay_proportion": 0.0,
#         "replay_buffer_num_slots": 100,
#         "learner_queue_size": 16,
#         "learner_queue_timeout": 30000,
#         "max_sample_requests_in_flight_per_worker": 2,
#         "broadcast_interval": 1,
#         "grad_clip": 40.0,
#         "opt_type": "adam",
#         "lr": 0.0005,
#         "lr_schedule": None,
#         "decay": 0.99,
#         "momentum": 0.0,
#         "epsilon": 0.1,
#         "vf_loss_coeff": 0.5,
#         "entropy_coeff": 0.01,
#         "entropy_coeff_schedule": None,
#         "input": (
#             lambda ioctx: PolicyServerInput(ioctx, args.ip, 44444)
#         ),
#         # Use a single worker process to run the server.
#         "num_workers": 1,
#         # Disable OPE, since the rollouts are coming from online clients.
#         "input_evaluation": [],
#         # "callbacks": MyCallbacks,
#         "env_config": {"sleep": True, "framework": 'tf'},
#         "framework": "tfe",
#         "eager_tracing": True,
#         # "explore": True,
#         # "exploration_config": {
#         #     "type": "Curiosity",  # <- Use the Curiosity module for exploring.
#         #     "eta": 1.0,  # Weight for intrinsic rewards before being added to extrinsic ones.
#         #     "lr": 0.001,  # Learning rate of the curiosity (ICM) module.
#         #     "feature_dim": 288,  # Dimensionality of the generated feature vectors.
#         #     # Setup of the feature net (used to encode observations into feature (latent) vectors).
#         #     "feature_net_config": {
#         #         "fcnet_hiddens": [],
#         #         "fcnet_activation": "relu",
#         #     },
#         #     "inverse_net_hiddens": [256],  # Hidden layers of the "inverse" model.
#         #     "inverse_net_activation": "relu",  # Activation of the "inverse" model.
#         #     "forward_net_hiddens": [256],  # Hidden layers of the "forward" model.
#         #     "forward_net_activation": "relu",  # Activation of the "forward" model.
#         #     "beta": 0.2,  # Weight for the "forward" loss (beta) over the "inverse" loss (1.0 - beta).
#         #     # Specify, which exploration sub-type to use (usually, the algo's "default"
#         #     # exploration, e.g. EpsilonGreedy for DQN, StochasticSampling for PG/SAC).
#         #     "sub_exploration": {
#         #         "type": "StochasticSampling",
#         #     }
#         # },
#         "_fake_gpus": True
#     },
#     _allow_unknown_configs=True,
# )




ray.init()

print(f"running on: {args.ip}:44444")

# trainer = DDPPOTrainer(config=DEFAULT_CONFIG)
trainer = PPOTrainer(config=DEFAULT_CONFIG, env=UnderlordEnv)
# trainer = APPOTrainer(config=DEFAULT_CONFIG, env=UnderlordEnv)

# checkpoint_path = CHECKPOINT_FILE.format(args.run)
checkpoint_path = "checkpointsE/"


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
